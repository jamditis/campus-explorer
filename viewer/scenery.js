// Scenery the export leaves to the viewer: per-tree level of detail (trees.js), far-field trees and land
// cover on the 4 km ground, trees lowered onto the ground, grass tufts near the camera, and the swap
// between full tiles and their far versions. Everything here runs only when the camera moved, so a still
// view costs nothing.
import * as THREE from 'three';
import { createTrees } from '../trees.js';

const REFRESH_MS = 250;            // tree and far-version updates while the camera moves
const GRASS_N = 6000, GRASS_R = 18; // tufts, and the radius they cover around the camera (m)
const GRASS_MAX_HEIGHT = 14;       // no tufts when the camera is higher than this above the ground
const GRASS_RETRIES = 30, GRASS_RETRY_MS = 1000; // asking again while the ground under the camera has no collision yet
const DOWN = new THREE.Vector3(0, -1, 0);

/**
 * @param app the shared app object (see docs/VIEWER.md)
 * @returns {{ prepare(root, tile, opts): void, release(root): void, trees: object, readonly grass: number }}
 */
export function createScenery(app) {
  const { scene, camera } = app;
  const trees = createTrees(scene, camera);
  let manifest = null, base = '', moved = true, last = 0, run = 0;

  // ---- land cover (from OpenStreetMap, tools/web-export/landcover.py) draped over the 4 km skirt ----
  function applyLandcover(root, url, half) {
    const tex = new THREE.TextureLoader().load(url, () => app.invalidate());
    tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.flipY = false;
    root.updateMatrixWorld(true);
    const v = new THREE.Vector3();
    root.traverse(o => {
      if (!o.isMesh || !/skirt/i.test(o.name + (o.parent?.name || ''))) return;
      const p = o.geometry.attributes.position, uv = new Float32Array(p.count * 2);
      for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld); uv[i * 2] = (v.x + half) / (2 * half); uv[i * 2 + 1] = (v.z + half) / (2 * half); }
      o.geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
      // lifted to the campus lawn's brightness so the modelled ground does not end in a hard tonal edge
      o.material = new THREE.MeshStandardMaterial({ map: tex, color: new THREE.Color(1.35, 1.35, 1.28), roughness: 0.95, envMapIntensity: 0.3 });
    });
  }

  /** Called by the world for every tile, and for every far version, before it joins the scene. */
  function prepare(root, tile, { far = false } = {}) {
    app.look.decorate(root);
    if (far) return;
    if (tile.file === 'far_houses.glb') root.traverse(o => { if (o.material) { o.material.envMapIntensity = 0.25; o.material.roughness = 0.95; } });
    if (tile.file === 'skirt.glb' && manifest?.landcover) applyLandcover(root, base + manifest.landcover.file, manifest.landcover.half);
  }
  function release(root) { trees.remove(root); }

  // ---- trees ----
  // Instanced trees whose trunk base hangs over the ground (edge street trees placed for the Blender far-field
  // geometry) are lowered onto it. Only ever lowers, and only gaps of 0.8 to 25 m. It needs the ground under
  // every tree, so it runs once the full campus is in, a few trees per idle slice.
  const _o = new THREE.Vector3();
  function settleTrees(my) {
    const pending = [];
    trees.settle((b, g) => { if (g.list.some(o => /^(Tree_|T_)/.test(o.name)) && !g.settled) pending.push({ b, g }); return 0; });
    const gaps = new Map(); let i = 0;
    const slice = deadline => {
      if (my !== run) return;
      while (i < pending.length && deadline.timeRemaining() > 3) {
        const { b } = pending[i++];
        const hit = app.world.raycast(_o.set(b.x, b.y + 40, b.z), DOWN, 800, { bigOnly: true });
        const gap = hit ? b.y - hit.point.y : 0;
        if (gap > 0.8 && gap < 25) gaps.set(b, gap);
      }
      if (i < pending.length) { idle(slice); return; }
      for (const { g } of pending) g.settled = true;
      const n = trees.settle(b => gaps.get(b) ?? 0);
      if (n) { app.look.invalidateShadows(); app.invalidate(); }
      window.__campusSnapped = n;
    };
    idle(slice);
  }
  const idle = fn => (window.requestIdleCallback ? requestIdleCallback(fn, { timeout: 500 }) : setTimeout(() => fn({ timeRemaining: () => 8 }), 30));

  // ---- grass tufts near the camera on lawn surfaces (Medium and High), scattered again as you move ----
  const grass = (() => {
    const pos = [], col = [], nrm = [];
    for (let i = 0; i < 7; i++) {
      const a = Math.random() * Math.PI * 2, r = Math.random() * 0.12, x = Math.cos(a) * r, z = Math.sin(a) * r;
      const w = 0.012 + Math.random() * 0.01, h = 0.1 + Math.random() * 0.16, lean = (Math.random() - 0.5) * 0.1, d = Math.random() * Math.PI;
      const dx = Math.cos(d) * w, dz = Math.sin(d) * w;
      pos.push(x - dx, 0, z - dz, x + dx, 0, z + dz, x + lean, h, z + lean * 0.5);
      col.push(0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 1.1, 1.1, 0.9); nrm.push(0, 1, 0, 0, 1, 0, 0, 1, 0);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3));
    const mesh = new THREE.InstancedMesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, side: THREE.DoubleSide, roughness: 0.95, envMapIntensity: 0.3 }), GRASS_N);
    mesh.count = 0; mesh.frustumCulled = false; mesh.receiveShadow = true; mesh.name = 'grass_tufts'; scene.add(mesh); return mesh;
  })();
  let grassAt = null, grassJob = null, grassRetry = 0, grassTries = 0;
  const _m4 = new THREE.Matrix4(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _col = new THREE.Color(), _from = new THREE.Vector3();
  const hideGrass = () => { if (grass.visible) { grass.visible = false; app.invalidate(); } };
  // Decide whether to scatter again. Only ground whose collision is already built is asked, so this never stalls.
  function checkGrass() {
    if (app.lite || app.look.quality === 'low' || !app.state.ready) { hideGrass(); return; }
    const c = camera.position;
    const under = app.world.raycast(_from.set(c.x, c.y + 2, c.z), DOWN, 800, { builtOnly: true });
    if (!under) {
      // The collision under a still camera is built in idle time. Look again shortly, a few times, when the
      // camera is low enough for tufts to matter.
      hideGrass();
      const low = isFinite(app.bounds.max.y) && c.y < app.bounds.max.y + GRASS_MAX_HEIGHT;
      grassRetry = low && grassTries++ < GRASS_RETRIES ? performance.now() + GRASS_RETRY_MS : 0;
      return;
    }
    grassRetry = 0; grassTries = 0;
    if (c.y - under.point.y > GRASS_MAX_HEIGHT) { hideGrass(); return; }
    if (!grass.visible) { grass.visible = true; app.invalidate(); }
    if (grassAt && Math.hypot(c.x - grassAt.x, c.z - grassAt.z) < 5) return;
    grassAt = c.clone();
    grassJob = { c: c.clone(), top: under.point.y + 25, i: 0, n: 0 };
  }
  // Scattering is spread over frames, up to 7 ms each.
  function grassStep() {
    const j = grassJob, t0 = performance.now();
    while (j.i < GRASS_N * 1.6 && j.n < GRASS_N && performance.now() - t0 < 7) {
      j.i++;
      const r = GRASS_R * Math.sqrt(Math.random()), a = Math.random() * Math.PI * 2;
      const hit = app.world.raycast(_from.set(j.c.x + Math.cos(a) * r, j.top, j.c.z + Math.sin(a) * r), DOWN, 800, { builtOnly: true });
      const m = hit && [].concat(hit.object.material)[0];
      if (!m || m.userData.tp !== 'grass' || hit.normal.y < 0.7) continue;
      _q.setFromAxisAngle(DOWN, Math.random() * Math.PI * 2); const k = 0.7 + Math.random() * 0.8; _s.set(k, k * (0.8 + Math.random() * 0.5), k);
      _m4.compose(hit.point, _q, _s); grass.setMatrixAt(j.n, _m4);
      _col.copy(m.color).multiplyScalar(1.5 + Math.random() * 0.6); grass.setColorAt(j.n, _col); j.n++;
    }
    grass.count = Math.max(grass.count, j.n); grass.instanceMatrix.needsUpdate = true; if (grass.instanceColor) grass.instanceColor.needsUpdate = true;
    if (j.i >= GRASS_N * 1.6 || j.n >= GRASS_N) { grass.count = j.n; grassJob = null; }
    app.invalidate();
  }

  // ---- wiring ----
  app.on('scene:start', e => {
    manifest = e.manifest; base = e.base; run++;
    trees.reset(); grass.count = 0; grassAt = null; grassJob = null; grassRetry = 0; grassTries = 0; moved = true;
  });
  // trees.add refreshes the tree instances itself. No redraw is asked for here: the world asks for a lazy one,
  // and an immediate redraw (with a fresh shadow map) for every arriving tile holds up loading on a slow GPU.
  app.on('tile', ({ tile }) => {
    trees.add(tile.root);
    // the new tile may be the ground under the camera: let the grass check ask again (one cheap ray, no redraw)
    grassTries = 0; grassRetry = performance.now() + GRASS_RETRY_MS;
  });
  app.on('scene:complete', () => {
    const my = run;
    if (app.world.budget !== Infinity) return; // lite profile: the ground under far trees is not in memory
    settleTrees(my);
    if (manifest?.far_trees) {
      fetch(base + manifest.far_trees).then(r => r.arrayBuffer())
        .then(b => { if (my === run) { trees.addFar(new Float32Array(b)); app.invalidate(); } })
        .catch(e => console.warn('far trees did not load', e));
    }
  });
  app.on('quality', ({ name }) => { trees.setQuality(name); moved = true; grassAt = null; });
  // Refresh in the same frame as the camera change (the `camera` event comes before the draw), at most every
  // REFRESH_MS; a change that came too soon after the last refresh is picked up on a later frame.
  function refresh(time) {
    moved = false; last = time;
    trees.update(true);
    app.world.updateLods(true);
    grassTries = 0;
    if (!grassJob) checkGrass();
    // trees entering the view need their shadows; the shadow map is only redrawn on request
    app.look.invalidateShadows(); app.invalidate();
  }
  app.on('camera', () => { const now = performance.now(); if (now - last >= REFRESH_MS) refresh(now); else moved = true; });
  app.on('frame', ({ time }) => {
    if (grassJob) grassStep();
    else if (grassRetry && time >= grassRetry) { grassRetry = 0; checkGrass(); }
    if (moved && time - last >= REFRESH_MS) refresh(time);
  });

  return { prepare, release, trees, get grass() { return grass.count; } };
}
