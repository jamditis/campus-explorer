// Streams the GLB tiles of the campus (models/manifest.json) and owns the collision index.
// The view is usable after the far-field ground and the nearest tiles; the rest load nearest-first
// around whatever the user is looking at. BVHs are built per mesh the first time a ray needs them.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { MeshBVH, CENTER, acceleratedRaycast } from 'three-mesh-bvh';
import { orderTiles, firstBatch, tileAt, boundsOf, squareDistance } from './schedule.js';
import { shows } from './ownership.js';

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

  // ---- ownership: which model owns each 2 m cell of ground (see tools/web-export/unify.mjs) ----
  let own = null; // { data, w, h, x0, z0, cell, values, texture }
  async function loadOwnership(o) {
    own = null; if (!o) return null;
    // the grey levels are data: decode without colour management
    const blob = await (await fetch(base + o.file, { signal: abort?.signal })).blob();
    const img = await createImageBitmap(blob, { colorSpaceConversion: 'none', premultiplyAlpha: 'none' });
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
    const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(img, 0, 0);
    const rgba = g.getImageData(0, 0, c.width, c.height).data, data = new Uint8Array(c.width * c.height);
    for (let i = 0; i < data.length; i++) data[i] = rgba[i * 4];
    const texture = new THREE.DataTexture(data, c.width, c.height, THREE.RedFormat); texture.needsUpdate = true; // nearest filter, no mipmaps
    own = { data, w: c.width, h: c.height, x0: o.x0, z0: o.z0, cell: o.cell, values: o.values, texture, box: o };
    return own;
  }
  const tilesAt = (x, z) => tiles.filter(t => t.center && squareDistance(t, x, z) === 0);
  /** Ownership value of the cell at (x, z); 0 outside the map. */
  function ownerAt(x, z) {
    if (!own) return 0;
    const c = Math.floor((x - own.x0) / own.cell), r = Math.floor((z - own.z0) / own.cell);
    return c < 0 || r < 0 || c >= own.w || r >= own.h ? 0 : own.data[r * own.w + c];
  }
  /** Is a surface of this model drawn, and so solid, at (x, z)? The same rule as the shaders (viewer/ownership.js). */
  const solidAt = (group, x, z) => !own || shows(group, ownerAt(x, z));
  const urgent = new Set();
  const progress = { loaded: 0, total: 1, tiles: 0, count: 0 };

  function free(root) {
    const mats = new Set();
    root.traverse(o => {
      if (!o.isMesh) return;
      o.geometry.boundsTree = null; o.geometry.dispose();
      for (const m of [].concat(o.material)) if (m) mats.add(m);
    });
    for (const m of mats) { for (const k of MATERIAL_MAPS) m[k]?.dispose(); m.dispose(); }
  }
  function dispose() {
    abort?.abort(); abort = null; clearInterval(watch);
    free(group);
    scene.remove(group); group = new THREE.Group(); group.name = 'campus'; scene.add(group);
    tiles = []; colliders = []; urgent.clear(); paused = false; resume = null; budget = Infinity; pumping = false;
    own?.texture.dispose(); own = null;
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
    for (let i = from; i < colliders.length; i++) { colliders[i].tile = tile; colliders[i].group = tile.scene; }
  }
  function collect(root) {
    root.traverse(o => {
      // not `visible`: screen-size culling flips that every frame
      if (!o.isMesh || o.isInstancedMesh || o.userData.filler) return;
      const m = Array.isArray(o.material) ? o.material[0] : o.material;
      if (m?.userData.leaf || m?.userData.glass) return; // you walk through foliage and look through glass
      const g = o.geometry; if (!g.boundingBox) g.computeBoundingBox();
      const tris = (g.index ? g.index.count : g.attributes.position.count) / 3;
      if (tris > SPLIT_TRIS && g.index) for (const part of splitByCell(o)) colliders.push(part);
      else colliders.push({ mesh: o, box: g.boundingBox.clone().applyMatrix4(o.matrixWorld), tris });
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
      const gltf = await loader.parseAsync(buf, base);
      if (my !== token) return;
      const root = gltf.scene; root.name = tile.file.replace('.glb', '').split('/').pop();
      prepare(root, tile);
      root.updateMatrixWorld(true);
      // compile this tile's shaders before it joins the scene, so adding it does not stall a frame
      try { await renderer.compileAsync(root, camera, scene); } catch { /* compiled on first draw instead */ }
      if (my !== token) { free(root); release(root); return; }
      group.add(root); tile.root = root; tile.state = 'ready';
      if (tile.center) app.bounds.expandByObject(root);
      addColliders(root, tile);
      warmIdle(); // collision near the view gets ready in idle time, so picks and the elevation readout do not wait
      progress.tiles++;
      app.emit('tile', { tile }); app.emit('progress', progress); app.invalidate();
    } catch (e) {
      if (my !== token || e.name === 'AbortError') return;
      progress.loaded += tile.bytes - tile.got; // keep the bar honest when a tile fails
      tile.state = 'error'; tile.error = e;
      console.error(e);
      app.emit('tile:error', { tile, error: e });
    }
  }

  // ---- memory budget (phones): keep only the tiles nearest the view ----
  const _focus = new THREE.Vector3(), _dir = new THREE.Vector3(), _last = new THREE.Vector3(Infinity, 0, 0);
  /** The centred tiles that should be in memory now, or null when there is no budget. `slack` widens the set. */
  function wanted(slack = 0) {
    if (budget === Infinity) return null;
    app.focus(_focus);
    const set = new Set(orderTiles(tiles.filter(t => t.center), { x: _focus.x, z: _focus.z }).slice(0, budget + slack));
    for (const t of urgent) set.add(t);
    return set;
  }
  function evict(tile) {
    group.remove(tile.root); free(tile.root); release(tile.root);
    colliders = colliders.filter(c => c.tile !== tile);
    tile.root = null; tile.state = 'queued'; progress.tiles--; progress.loaded -= tile.bytes;
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
    base = './models/';
    const man = await (await fetch(base + 'manifest.json', { cache: 'no-cache', signal: abort.signal })).json();
    if (my !== token) return;
    let list = man.tiles.filter(t => skirt || !t.file.endsWith('skirt.glb')).map(t => ({ ...t, state: 'queued', root: null, got: 0 }));
    const b = boundsOf(list);
    const at = focus ?? (b ? { x: (b.minX + b.maxX) / 2, z: (b.minZ + b.maxZ) / 2 } : { x: 0, z: 0 });
    if (limit < Infinity) {
      const keep = new Set(orderTiles(list.filter(t => t.center), at).slice(0, limit));
      list = list.filter(t => !t.center || keep.has(t));
    }
    tiles = list; budget = cap;
    app.bounds.makeEmpty();
    if (b) app.bounds.set(new THREE.Vector3(b.minX, Infinity, b.minZ), new THREE.Vector3(b.maxX, -Infinity, b.maxZ));
    Object.assign(progress, { loaded: 0, total: tiles.reduce((s, t) => s + t.bytes, 0), tiles: 0, count: tiles.length });
    const ownership = await loadOwnership(man.ownership).catch(e => { console.error('ownership map did not load', e); return null; });
    if (my !== token) return;
    app.emit('scene:start', { manifest: man, focus: at, ownership });

    const first = firstBatch(tiles, at, FIRST_TILES);
    progress.first = first.reduce((s, t) => s + t.bytes, 0);
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
  }
  /** Drop the memory budget and load every tile. */
  async function loadAll() {
    if (budget === Infinity) return;
    budget = Infinity; clearInterval(watch); app.emit('progress', progress);
    await pump(token);
  }

  // The proxy stand-ins are not in the scene graph: drop their BVHs with the scene.
  function home(at) { app.home ??= new THREE.Vector3(at.x, 0, at.z); }

  // ---- collision ----
  function ensureBVH(c) {
    const g = c.mesh.geometry;
    if (!g.boundsTree) g.boundsTree = new MeshBVH(g, { strategy: CENTER, maxLeafTris: 12, indirect: true });
    return g.boundsTree;
  }
  const ray = new THREE.Raycaster(); ray.firstHitOnly = true;
  const _p = new THREE.Vector3(), _hits = [], _n = new THREE.Vector3(), _cand = [];

  /**
   * First solid surface along a ray, in world space.
   * `builtOnly` skips meshes whose BVH is not built yet (never stalls; may miss).
   */
  function raycast(origin, dir, far = Infinity, { builtOnly = false } = {}) {
    ray.set(origin, dir); ray.near = 0;
    _cand.length = 0;
    for (const c of colliders) {
      if ((builtOnly && !c.mesh.geometry.boundsTree)) continue;
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
      const limit = best ? best.distance : far;
      // a hit in a cell this model does not own is on hidden geometry: step past it and look again
      let h = null, skipped = 0;
      for (let tries = 0; tries < 6; tries++) {
        ray.far = limit - skipped; _hits.length = 0;
        c.mesh.raycast(ray, _hits);
        h = _hits[0] ?? null;
        if (!h || solidAt(c.group, h.point.x, h.point.z)) break;
        skipped += h.distance + 0.02; ray.ray.origin.copy(origin).addScaledVector(dir, skipped); h = null;
      }
      ray.ray.origin.copy(origin);
      if (h) { h.distance += skipped; if (!best || h.distance < best.distance) best = h; }
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
  const _tp = new THREE.Vector3(), _cp = new THREE.Vector3(), _tn = new THREE.Vector3(), _wp = new THREE.Vector3();
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
          // a wall the ownership map hides is not there: test where the capsule touches it, not where the walker stands
          if (own && (_wp.copy(_tp).applyMatrix4(mw), !solidAt(c.group, _wp.x, _wp.z))) return;
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
    ownerAt, solidAt,
    get tiles() { return tiles; },
    get group() { return group; },
    get progress() { return progress; },
    get paused() { return paused; },
    resume() { resume?.(); resume = null; },
    // a square can hold one tile from each model
    isLoaded(x, z) { return tilesAt(x, z).every(t => t.state === 'ready' || t.state === 'error'); },
    prioritize(x, z) {
      for (const t of tilesAt(x, z)) if (t.state === 'queued') urgent.add(t);
      if (paused && urgent.size) pump(token); // nothing else is pumping while the download is on hold
    },
    tileAt: (x, z) => tileAt(tiles, x, z),
  };
}
