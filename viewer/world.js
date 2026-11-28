// Streams the GLB tiles of the campus (models/main/manifest.json) and owns the collision index.
// The view is usable after the far-field ground and the nearest tiles; the rest load nearest-first
// around whatever the user is looking at. BVHs are built per mesh the first time a ray needs them.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { MeshBVH, CENTER, acceleratedRaycast } from 'three-mesh-bvh';
import { orderTiles, firstBatch, tileAt, boundsOf, squareDistance } from './schedule.js';
import { dirOf, resolveUri, imageUri, textureKey, createTextureShare, sharedBytes, newBytes } from './texshare.js';
import { inCampusBox } from './pose-math.js';
import { withFullRange } from './treelod-math.js';

THREE.Mesh.prototype.raycast = acceleratedRaycast;

const FIRST_TILES = 4;       // centred tiles that must be in before the view is shown
const PARALLEL = 3;          // tile downloads at once while streaming
const SPLIT_TRIS = 200000;   // bigger meshes are split into ground cells, so one BVH build never freezes the page
const CELL = 96;             // metres per collision cell
const MATERIAL_MAPS = ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap', 'alphaMap'];
const idle = fn => (window.requestIdleCallback ? requestIdleCallback(fn, { timeout: 500 }) : setTimeout(() => fn({ timeRemaining: () => 8 }), 60));

/**
 * @param app the shared app object (see docs/VIEWER.md)
 * @param prepare called with (root, tile) once per tile before it is added: materials, textures, culling
 * @param release called with (root) when a tile is dropped from memory
 */
export function createWorld(app, prepare, release = () => {}) {
  const { renderer, scene, camera } = app;
  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  // geometry decoding off the main thread keeps orbiting smooth while tiles stream in
  MeshoptDecoder.useWorkers?.(Math.max(1, Math.min(3, (navigator.hardwareConcurrency || 4) - 1)));

  let group = new THREE.Group(); group.name = 'campus'; scene.add(group);
  let tiles = [], colliders = [], token = 0, abort = null, base = '', paused = false, resume = null;
  let budget = Infinity, pumping = false, watch = 0;

  const tilesAt = (x, z) => tiles.filter(t => t.center && squareDistance(t, x, z) === 0);
  const urgent = new Set();
  const progress = { loaded: 0, total: 1, tiles: 0, count: 0 };
  // images several tiles share (models/main/tex/): one texture for all of them, and their bytes counted once
  const textures = createTextureShare();
  let texSizes = {}, texSeen = new Set();

  function free(root) {
    const mats = new Set();
    root.traverse(o => {
      if (!o.isMesh) return;
      o.geometry.boundsTree = null; o.geometry.dispose();
      for (const m of [].concat(o.material)) if (m) mats.add(m);
    });
    for (const m of mats) { for (const k of MATERIAL_MAPS) if (!textures.has(m[k])) m[k]?.dispose(); m.dispose(); }
    textures.release(root); // a shared texture goes with the last tile that uses it
  }
  function dispose() {
    abort?.abort(); abort = null; clearInterval(watch); clearTimeout(lodTimer); lodTimer = 0; lodTimerAt = Infinity;
    free(group); textures.clear(); texSeen = new Set();
    scene.remove(group); group = new THREE.Group(); group.name = 'campus'; scene.add(group);
    tiles = []; colliders = []; lods = []; urgent.clear(); paused = false; resume = null; budget = Infinity; pumping = false;
    Object.assign(progress, { loaded: 0, total: 1, tiles: 0, count: 0 });
  }

  async function download(tile, signal) {
    const res = await fetch(base + tile.file, { signal });
    if (!res.ok) throw new Error(`${tile.file}: HTTP ${res.status}`);
    if (!res.body) return res.arrayBuffer();
    const reader = res.body.getReader(), chunks = [];
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value); tile.got += value.byteLength; progress.loaded += value.byteLength;
      app.emit('progress', progress);
    }
    return new Blob(chunks).arrayBuffer();
  }

  function addColliders(root, tile) {
    const from = colliders.length;
    collect(root);
    for (let i = from; i < colliders.length; i++) colliders[i].tile = tile;
  }
  function collect(root) {
    root.traverse(o => {
      // not `visible`: screen-size culling flips that every frame
      if (!o.isMesh || o.isInstancedMesh || o.userData.filler) return;
      const m = Array.isArray(o.material) ? o.material[0] : o.material;
      if (m?.userData.leaf || m?.userData.glass) return; // you walk through foliage and look through glass
      const g = o.geometry; if (!g.boundingBox) g.computeBoundingBox();
      const tris = (g.index ? g.index.count : g.attributes.position.count) / 3;
      const box = g.boundingBox.clone().applyMatrix4(o.matrixWorld);
      // `big`: wide and not tall, so ground, paving or a roof rather than a post or a bench (see raycast's bigOnly)
      const big = Math.max(box.max.x - box.min.x, box.max.z - box.min.z) > 15 && box.max.y - box.min.y < 150;
      if (tris > SPLIT_TRIS && g.index) for (const part of splitByCell(o)) { part.big = big; colliders.push(part); }
      else colliders.push({ mesh: o, box, tris, big });
    });
  }

  // A terrain mesh can hold millions of triangles. Bucket them by ground cell into stand-in meshes that
  // share the vertex buffer; each cell gets its own small BVH, built only if a ray goes there.
  function splitByCell(mesh) {
    const g = mesh.geometry, pos = g.attributes.position, index = g.index.array, e = mesh.matrixWorld.elements;
    const v = new THREE.Vector3(), cells = new Map(), n = index.length / 3, keys = new Int32Array(n);
    for (let t = 0; t < n; t++) {
      v.fromBufferAttribute(pos, index[t * 3]);
      // world x and z of the triangle's first corner are enough to pick a cell
      const x = e[0] * v.x + e[4] * v.y + e[8] * v.z + e[12], z = e[2] * v.x + e[6] * v.y + e[10] * v.z + e[14];
      const key = (Math.floor(x / CELL) + 2048) * 4096 + Math.floor(z / CELL) + 2048;
      keys[t] = key; cells.set(key, (cells.get(key) ?? 0) + 1);
    }
    const parts = new Map();
    for (const [key, count] of cells) parts.set(key, { array: new Uint32Array(count * 3), at: 0 });
    for (let t = 0; t < n; t++) {
      const part = parts.get(keys[t]);
      part.array[part.at++] = index[t * 3]; part.array[part.at++] = index[t * 3 + 1]; part.array[part.at++] = index[t * 3 + 2];
    }
    const out = [];
    for (const { array } of parts.values()) {
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', pos); geo.setIndex(new THREE.BufferAttribute(array, 1));
      const box = new THREE.Box3();
      for (let i = 0; i < array.length; i++) box.expandByPoint(v.fromBufferAttribute(pos, array[i]));
      geo.boundingBox = box.clone(); geo.boundingSphere = box.getBoundingSphere(new THREE.Sphere());
      const stand = new THREE.Mesh(geo, mesh.material); stand.matrixAutoUpdate = false; stand.matrixWorld.copy(mesh.matrixWorld); stand.name = mesh.name;
      out.push({ mesh: stand, box: box.applyMatrix4(mesh.matrixWorld), tris: array.length / 3 });
    }
    return out;
  }

  async function loadTile(tile, my) {
    tile.state = 'loading'; tile.got = 0;
    try {
      const buf = await download(tile, abort.signal);
      const path = base + dirOf(tile.file); // image URIs are relative to the tile's own folder
      const gltf = await loader.parseAsync(buf, path);
      if (my !== token) return;
      const root = gltf.scene; root.name = tile.file.replace('.glb', '').split('/').pop();
      shareTextures(gltf, root, path);
      strip(root); dropUnmaterialled(gltf);
      prepare(root, tile, { far: false });
      root.updateMatrixWorld(true);
      // compile this tile's shaders before it joins the scene, so adding it does not stall a frame
      try { await renderer.compileAsync(root, camera, scene); } catch { /* compiled on first draw instead */ }
      if (my !== token) { free(root); release(root); return; }
      group.add(root); tile.root = root; tile.state = 'ready';
      if (tile.far) updateLods(true); // hide the far version that stood in for it
      if (tile.center) expandBounds(root);
      addColliders(root, tile);
      warmIdle(); // collision near the view gets ready in idle time, so picks and the elevation readout do not wait
      progress.tiles++; progress.loaded += newBytes(tile, texSeen, texSizes);
      app.emit('tile', { tile }); app.emit('progress', progress); app.invalidate(true); // lazy: see app.invalidate
    } catch (e) {
      if (my !== token || e.name === 'AbortError') return;
      progress.loaded += tile.bytes - tile.got + newBytes(tile, texSeen, texSizes); // keep the bar honest when a tile fails
      tile.state = 'error'; tile.error = e;
      console.error(e);
      app.emit('tile:error', { tile, error: e });
    }
  }

  // The campus box (app.bounds) grows by the meshes of a centred tile, but not by far-field ground
  // (n_t_0_0.glb holds BD_farfield_3DEP_ortho, 2.3 km wide and down to y -54): its floor is the fallback
  // ground height of place moves and the base of the overview, and that mesh put both 150 m underground.
  const _mb = new THREE.Box3(), _ms = new THREE.Vector3();
  function expandBounds(root) {
    root.updateMatrixWorld(true);
    root.traverse(o => {
      if (!o.isMesh) return;
      _mb.setFromObject(o);
      if (!_mb.isEmpty() && inCampusBox(_mb.getSize(_ms))) app.bounds.union(_mb);
    });
  }

  // Ground of one source model that the other model's merge superseded (the manifest's `hide` list, written by
  // tools/web-export/make_chunks.py), e.g. a terrain feather lying across a north sports field.
  let hide = new Set();
  function strip(root) {
    if (!hide.size) return;
    const drop = [];
    root.traverse(o => { if (o.isMesh && hide.has(o.name)) drop.push(o); });
    for (const o of drop) { o.removeFromParent(); o.geometry.dispose(); }
  }

  // Geometry exported with no material at all gets three's plain white default. In practice that is a
  // geometry-nodes source left behind next to its own output (Curbs_granite_OSM: the curb curve's mesh lies
  // exactly on the CurbSweep granite curbs and z-fights into a white speckle) or a stray leaf card, so drop it.
  // A cloned default material carries an empty association, hence the `materials` index check.
  function dropUnmaterialled(gltf) {
    const drop = [];
    gltf.scene.traverse(o => { if (o.isMesh && ![].concat(o.material).some(m => gltf.parser.associations.get(m)?.materials !== undefined)) drop.push(o); });
    for (const o of drop) { o.removeFromParent(); o.geometry.dispose(); }
  }

  // A shared image (tex/, tools/web-export/share_tex.mjs) arrives as a new texture in every tile that names it.
  // Swap it for the texture an earlier tile already has, so the GPU holds one copy; the browser's cache serves
  // the file itself. Materials stay per tile; look.js sets only anisotropy on a texture, the same for every user.
  function shareTextures(gltf, root, path) {
    const { json, associations } = gltf.parser;
    root.traverse(o => {
      if (!o.isMesh) return;
      for (const m of [].concat(o.material)) {
        if (!m) continue;
        for (const k of MATERIAL_MAPS) {
          const t = m[k], i = t ? associations.get(t)?.textures : undefined, uri = i === undefined ? null : imageUri(json, i);
          if (uri) m[k] = textures.acquire(root, textureKey(resolveUri(path, uri), t), t);
        }
      }
    });
  }

  // ---- far versions of tiles (LOD) ----
  // A tile can ship a far version (lod/<tile>.glb from tools/web-export/lod.mjs: no instances, small parts or
  // interiors, about 0.5 m error). Past a distance set by the quality level, the full tile's plain meshes move
  // to layer 2 (not drawn, no shadows) and the far version takes layer 0. A far version also stands in for its
  // tile while the tile is not in memory: under a memory budget (phones) the evicted tiles stay in view that way.
  // Instanced trees stay with the full tile: trees.js culls and swaps those per instance. Collision and picks
  // always use the full tiles. Far versions load nearest-first once the first round of tiles is in, and stay.
  // A far version has no instanced trees; it carries stand-ins for them instead (scene extras `trees`, scenery.js).
  const LOD_DIST = { low: 260, medium: 420, high: 650 };
  const LOD_RETRY_MS = 20000, LOD_RETRY_MAX_MS = 300000; // a far version that failed is tried again, each wait twice the last, up to 5 min
  const LOD_FETCH_MS = 60000; // a far-version download that takes longer fails (and is tried again): no pass can hang
  let lodTimer = 0, lodTimerAt = Infinity, lodRetrying = 0; // the scene token of the retry pass that is running
  // One timer and one retry pass at a time for all failed far versions, each at its own wait: a connection that
  // drops makes every far version fail, and their retries must not all download at once when it comes back.
  function retryLater(my) {
    if (my !== token) return;
    const due = tiles.filter(t => t.lod && !t.far && !t.farLoading && t.farFails).map(t => t.farWait);
    if (!due.length) return;
    const at = Math.min(...due);
    if (lodTimer && at >= lodTimerAt) return; // the timer set already comes first
    clearTimeout(lodTimer); lodTimerAt = at;
    lodTimer = setTimeout(async () => {
      lodTimer = 0; lodTimerAt = Infinity;
      if (my !== token || lodRetrying === my) return; // the running retry pass calls retryLater when it ends
      lodRetrying = my;
      try { await loadLods(my); } finally { if (lodRetrying === my) lodRetrying = 0; }
      retryLater(my);
    }, Math.max(0, Math.min(...due) - performance.now()));
  }
  let lods = [], lodLast = 0;
  async function loadLods(my) {
    app.focus(_focus);
    for (const tile of orderTiles(tiles.filter(t => t.lod), { x: _focus.x, z: _focus.z })) {
      if (my !== token) return;
      if (tile.far || tile.farLoading || tile.farWait > performance.now()) continue; // loadAll can start a second pass while this one runs
      tile.farLoading = true;
      let root;
      try {
        const signal = AbortSignal.any && AbortSignal.timeout ? AbortSignal.any([abort.signal, AbortSignal.timeout(LOD_FETCH_MS)]) : abort.signal;
        const res = await fetch(base + tile.lod, { signal });
        if (!res.ok) throw new Error(`${tile.lod}: HTTP ${res.status}`);
        const path = base + dirOf(tile.lod);
        const g = await loader.parseAsync(await res.arrayBuffer(), path); dropUnmaterialled(g); root = g.scene;
        shareTextures(g, root, path);
      } catch (e) {
        tile.farLoading = false; tile.farFails = (tile.farFails ?? 0) + 1;
        const wait = Math.min(LOD_RETRY_MAX_MS, LOD_RETRY_MS * 2 ** (tile.farFails - 1));
        tile.farWait = performance.now() + wait;
        retryLater(my);
        if (e.name !== 'AbortError') console.warn('far version did not load', tile.lod, e);
        continue;
      }
      if (my !== token) { free(root); return; }
      root.name = `lod_${tile.file.replace('.glb', '').split('/').pop()}`;
      strip(root); // the far version carries the same objects as the full tile
      prepare(root, tile, { far: true });
      root.traverse(o => { if (o.isMesh) { o.userData.hidden = o.userData.lod = true; o.layers.set(2); } });
      group.add(root); tile.far = root;
      lods.push({ tile, lo: root, box: new THREE.Box3().setFromObject(root), root: null, hi: [], far: null });
      if (updateLods(true)) app.invalidate();
    }
  }
  /** Swap full tiles and far versions for the camera position and what is in memory. Returns true when something changed. */
  function updateLods(force = false) {
    const now = performance.now(); if (!force && now - lodLast < 250) return false; lodLast = now;
    const reach = LOD_DIST[app.look.quality] ?? LOD_DIST.medium; let changed = false;
    for (const l of lods) {
      const root = l.tile.state === 'ready' ? l.tile.root : null;
      if (root !== l.root) { // the full tile came into memory or left it
        l.root = root; l.hi = []; l.far = null;
        root?.traverse(o => { if (o.isMesh && !o.isInstancedMesh && !o.userData.treeLod) l.hi.push(o); });
      }
      const far = !root || l.box.distanceToPoint(camera.position) > reach;
      if (far === l.far) continue;
      l.far = far; changed = true;
      for (const o of l.hi) o.layers.set(far ? 2 : 0);
      l.lo.traverse(o => { if (o.isMesh) o.layers.set(far ? 0 : 2); });
    }
    return changed;
  }

  // ---- memory budget (phones): keep only the tiles nearest the view ----
  const _focus = new THREE.Vector3(), _dir = new THREE.Vector3(), _last = new THREE.Vector3(Infinity, 0, 0);
  /** The centred tiles that should be in memory now, or null when there is no budget. `slack` widens the set. */
  function wanted(slack = 0) {
    if (budget === Infinity) return null;
    app.focus(_focus);
    const set = new Set(orderTiles(tiles.filter(t => t.center), { x: _focus.x, z: _focus.z }).slice(0, budget + slack));
    // a tile with no far version has nothing to stand in for it, so it stays. The export leaves a far version out
    // where it would be empty or keep 80 % or more of the tile's plain triangles and draw calls (farWorthIt in
    // pack.mjs); instanced trees are not counted there. The 8 such tiles today hold 1.4 MB.
    for (const t of tiles) if (t.center && !t.lod) set.add(t);
    for (const t of urgent) set.add(t);
    return set;
  }
  function evict(tile) {
    group.remove(tile.root); free(tile.root); release(tile.root);
    colliders = colliders.filter(c => c.tile !== tile);
    tile.root = null; tile.state = 'queued'; progress.tiles--; progress.loaded -= tile.bytes;
    if (tile.far) updateLods(true); // its far version stands in
    app.emit('tile:gone', { tile });
  }
  async function pump(my) {
    if (pumping) return; pumping = true;
    const worker = async () => { for (let t; my === token && (t = nextTile());) await loadTile(t, my); };
    await Promise.all(Array.from({ length: PARALLEL }, worker));
    pumping = false;
  }
  // As the view moves, drop the tiles that fell out of range (two tiles of slack stop flip-flopping) and fetch the new ones.
  function rebalance(my) {
    if (my !== token || budget === Infinity || pumping) return;
    app.focus(_focus);
    if (_focus.distanceTo(_last) < 30 && !urgent.size) return;
    _last.copy(_focus);
    const keep = wanted(2); let gone = false;
    for (const t of tiles) if (t.center && t.state === 'ready' && !keep.has(t)) { evict(t); gone = true; }
    if (gone) { app.emit('progress', progress); app.invalidate(); }
    pump(my);
  }

  function nextTile() {
    const want = wanted();
    // while paused (data saver) only tiles someone asked for by name load
    const pending = tiles.filter(t => t.state === 'queued' && (paused ? urgent.has(t) : !want || !t.center || want.has(t)));
    if (!pending.length) return null;
    for (const t of pending) if (urgent.has(t)) { urgent.delete(t); return t; }
    app.focus(_focus); camera.getWorldDirection(_dir); _dir.y = 0;
    const dir = _dir.lengthSq() > 1e-6 ? _dir.normalize() : null;
    return orderTiles(pending, { x: _focus.x, z: _focus.z }, dir && { x: dir.x, z: dir.z })[0];
  }

  /**
   * Load the campus. Resolves when every tile is in (or failed). `limit` keeps only the N nearest centred tiles (testing).
   * `stream: false` stops after the first batch until `world.resume()` is called (data-saver connections).
   * `budget` caps how many centred tiles stay in memory (phones); `skirt: false` leaves out the far-field ground.
   */
  async function load({ limit = Infinity, stream = true, focus = null, budget: cap = Infinity, skirt = true } = {}) {
    dispose();
    const my = ++token; abort = new AbortController();
    base = './models/main/';
    const man = await (await fetch(base + 'manifest.json', { cache: 'no-cache', signal: abort.signal })).json();
    if (my !== token) return;
    let list = man.tiles.filter(t => skirt || !t.file.endsWith('skirt.glb')).map(t => ({ ...t, state: 'queued', root: null, got: 0 }));
    const b = boundsOf(list);
    const at = focus ?? (b ? { x: (b.minX + b.maxX) / 2, z: (b.minZ + b.maxZ) / 2 } : { x: 0, z: 0 });
    if (limit < Infinity) {
      const keep = new Set(orderTiles(list.filter(t => t.center), at).slice(0, limit));
      list = list.filter(t => !t.center || keep.has(t));
    }
    tiles = list; budget = cap; hide = new Set(man.hide || []); texSizes = man.tex || {};
    app.bounds.makeEmpty();
    if (b) app.bounds.set(new THREE.Vector3(b.minX, Infinity, b.minZ), new THREE.Vector3(b.maxX, -Infinity, b.maxZ));
    Object.assign(progress, { loaded: 0, total: tiles.reduce((s, t) => s + t.bytes, 0) + sharedBytes(tiles, texSizes), tiles: 0, count: tiles.length });
    app.emit('scene:start', { manifest: man, focus: at, base });

    const first = firstBatch(tiles, at, FIRST_TILES);
    progress.first = first.reduce((s, t) => s + t.bytes, 0) + sharedBytes(first, texSizes);
    await Promise.all(first.map(t => loadTile(t, my)));
    if (my !== token) return;
    if (first.length && first.every(t => t.state === 'error')) throw first[0].error;
    home(at);
    app.emit('scene:ready');

    if (!stream && tiles.some(t => t.state === 'queued')) {
      paused = true; app.emit('progress', progress);
      await new Promise(r => { resume = r; });
      if (my !== token) return;
      paused = false; app.emit('progress', progress);
      while (pumping) await new Promise(r => setTimeout(r, 100)); // a tile asked for during the pause is still arriving
      if (my !== token) return;
    }
    await pump(my);
    if (my !== token) return;
    app.emit('scene:complete');
    if (budget !== Infinity) watch = setInterval(() => rebalance(my), 600);
    loadLods(my);
  }
  /** Drop the memory budget and load every tile. */
  async function loadAll() {
    if (budget === Infinity) return;
    budget = Infinity; clearInterval(watch); app.emit('progress', progress);
    const my = token;
    await pump(my);
    if (my === token) loadLods(my);
  }

  // The proxy stand-ins are not in the scene graph: drop their BVHs with the scene.
  function home(at) { app.home ??= new THREE.Vector3(at.x, 0, at.z); }

  // ---- collision ----
  function ensureBVH(c) {
    const g = c.mesh.geometry;
    if (!g.boundsTree) g.boundsTree = withFullRange(g, () => new MeshBVH(g, { strategy: CENTER, maxLeafTris: 12, indirect: true }));
    return g.boundsTree;
  }
  const ray = new THREE.Raycaster(); ray.firstHitOnly = true;
  const _p = new THREE.Vector3(), _hits = [], _n = new THREE.Vector3(), _cand = [];

  /**
   * First solid surface along a ray, in world space.
   * `builtOnly` skips meshes whose BVH is not built yet (never stalls; may miss).
   * `bigOnly` keeps to wide surfaces (ground, paving, roofs) and ignores small objects.
   */
  function raycast(origin, dir, far = Infinity, { builtOnly = false, bigOnly = false } = {}) {
    ray.set(origin, dir); ray.near = 0;
    _cand.length = 0;
    for (const c of colliders) {
      if ((builtOnly && !c.mesh.geometry.boundsTree) || (bigOnly && !c.big)) continue;
      let enter = 0;
      if (!c.box.containsPoint(origin)) {
        if (!ray.ray.intersectBox(c.box, _p)) continue;
        enter = origin.distanceTo(_p);
      }
      if (enter <= far) _cand.push({ c, enter });
    }
    _cand.sort((a, b) => a.enter - b.enter);
    let best = null;
    for (const { c, enter } of _cand) {
      if (best && enter > best.distance) break;
      ensureBVH(c);
      ray.far = best ? best.distance : far; _hits.length = 0;
      c.mesh.raycast(ray, _hits); // straight to the mesh: layers do not apply, so far-swapped full tiles still collide
      const h = _hits[0];
      if (h && (!best || h.distance < best.distance)) best = h;
    }
    if (!best) return null;
    const normal = best.face ? _n.copy(best.face.normal).transformDirection(best.object.matrixWorld).clone() : new THREE.Vector3(0, 1, 0);
    if (normal.dot(dir) > 0) normal.negate(); // double-sided surfaces: face the ray
    return { point: best.point, normal, distance: best.distance, object: best.object };
  }

  const DOWN = new THREE.Vector3(0, -1, 0), _o = new THREE.Vector3();
  function groundAt(x, z, fromY = null, opts) {
    const top = fromY ?? (isFinite(app.bounds.max.y) ? app.bounds.max.y + 50 : 1000);
    const h = raycast(_o.set(x, top, z), DOWN, top + 500, opts);
    return h ? h.point.y : null;
  }

  const _mouse = new THREE.Vector2(), _pickRay = new THREE.Raycaster();
  function pick(clientX, clientY) {
    const r = app.canvas.getBoundingClientRect();
    _mouse.set(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1);
    _pickRay.setFromCamera(_mouse, camera);
    return raycast(_pickRay.ray.origin, _pickRay.ray.direction, 8000);
  }

  // ---- capsule against walls (walk mode) ----
  const _seg = new THREE.Line3(), _box = new THREE.Box3(), _lbox = new THREE.Box3(), _inv = new THREE.Matrix4();
  const _tp = new THREE.Vector3(), _cp = new THREE.Vector3(), _tn = new THREE.Vector3();
  /**
   * Push a vertical capsule (world space, `a` bottom sphere centre, `b` top) out of steep surfaces.
   * Adds the horizontal correction to `out` and returns true if it touched a wall. Floors are left to the ground ray.
   */
  function pushOut(a, b, radius, out) {
    _box.makeEmpty().expandByPoint(a).expandByPoint(b).expandByScalar(radius);
    let touched = false;
    for (const c of colliders) {
      if (!c.box.intersectsBox(_box)) continue;
      const bvh = ensureBVH(c), mw = c.mesh.matrixWorld;
      _inv.copy(mw).invert();
      const s = mw.getMaxScaleOnAxis(), r = radius / s;
      _seg.start.copy(a).add(out).applyMatrix4(_inv); _seg.end.copy(b).add(out).applyMatrix4(_inv);
      _lbox.makeEmpty().expandByPoint(_seg.start).expandByPoint(_seg.end).expandByScalar(r);
      let hit = false;
      bvh.shapecast({
        intersectsBounds: box => box.intersectsBox(_lbox),
        intersectsTriangle: tri => {
          tri.getNormal(_tn).transformDirection(mw);
          if (Math.abs(_tn.y) > 0.6) return; // floor or soffit
          const d = tri.closestPointToSegment(_seg, _tp, _cp);
          if (d >= r) return;
          _cp.sub(_tp); _cp.y = 0; // walls only push sideways
          if (_cp.lengthSq() < 1e-12) return;
          _cp.normalize().multiplyScalar(r - d);
          _seg.start.add(_cp); _seg.end.add(_cp); hit = true;
        },
      });
      if (!hit) continue;
      // the moved segment start, back in world space, minus where the capsule began
      _tp.copy(_seg.start).applyMatrix4(mw).sub(a);
      out.x = _tp.x; out.z = _tp.z; touched = true;
    }
    return touched;
  }

  /** Build the BVHs within `radius` metres of a point, yielding between meshes so the page stays alive. */
  async function warm(x, z, radius = 60) {
    const my = token;
    _box.set(new THREE.Vector3(x - radius, -Infinity, z - radius), new THREE.Vector3(x + radius, Infinity, z + radius));
    const todo = colliders.filter(c => !c.mesh.geometry.boundsTree && c.box.intersectsBox(_box));
    for (const c of todo) {
      if (my !== token) return;
      ensureBVH(c);
      await new Promise(r => setTimeout(r));
    }
  }
  // Build the BVHs within WARM_RADIUS of the view, nearest first, while the view is still, so picks rarely stall.
  // The rest of the campus stays unbuilt until someone looks there: BVHs for everything would cost hundreds of MB.
  const WARM_RADIUS = 250;
  let warming = false;
  app.on('camera', () => warmIdle());
  function warmIdle() {
    if (warming) return; warming = true;
    const my = token;
    const tick = deadline => {
      if (my !== token) { warming = false; return; }
      app.focus(_focus);
      let next = null, nd = Infinity;
      for (const c of colliders) {
        if (c.mesh.geometry.boundsTree) continue;
        const d = c.box.distanceToPoint(_focus) + c.tris * 1e-4; // near and small first
        if (d < nd) { nd = d; next = c; }
      }
      if (!next || nd > WARM_RADIUS) { warming = false; return; }
      if (deadline.timeRemaining() > 4 && app.isIdle()) ensureBVH(next);
      idle(tick);
    };
    idle(tick);
  }

  return {
    load, loadAll, dispose, raycast, groundAt, pick, pushOut, warm,
    get budget() { return budget; },
    updateLods, get lods() { return lods.length; },
    get tiles() { return tiles; },
    get group() { return group; },
    get progress() { return progress; },
    get paused() { return paused; },
    resume() { resume?.(); resume = null; },
    // a square can hold more than one tile (the two source models overlap in places)
    isLoaded(x, z) { return tilesAt(x, z).every(t => t.state === 'ready' || t.state === 'error'); },
    prioritize(x, z) {
      for (const t of tilesAt(x, z)) if (t.state === 'queued') urgent.add(t);
      if (paused && urgent.size) pump(token); // nothing else is pumping while the download is on hold
    },
    tileAt: (x, z) => tileAt(tiles, x, z),
  };
}
