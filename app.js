// Montclair State campus · working model — static three.js viewer (no build step).
// Tiles: ./models/main/manifest.json lists GLB tiles (meshopt-compressed, webp textures).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { createTrees } from './trees.js';
import { createLook } from './look.js';
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from 'three-mesh-bvh';
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;

const $ = id => document.getElementById(id);
const canvas = $('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: new URLSearchParams(location.search).has('capture') });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setPixelRatio(1);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.3, 20000);
const look = createLook(renderer, scene, camera);
const trees = createTrees(scene, camera);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.08; controls.maxPolarAngle = Math.PI * 0.495;
controls.minDistance = 3; controls.maxDistance = 6000; controls.screenSpacePanning = false;

let campus = new THREE.Group(); scene.add(campus);
const MAIN_CORE = new THREE.Box3(new THREE.Vector3(-420, 95, -300), new THREE.Vector3(330, 150, 420));
let core = MAIN_CORE.clone(), loaded = false, mode = 'orbit', view = 'first';
const colliders = []; let bvhReady = false;

function resize() { const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); look.resize(); }
addEventListener('resize', resize); resize();

// far-field filler crowns/trunks: hidden when the scene has no far-field skirt tile to stand on
let hasSkirt = false;
const FILLER = /^(WS62_crown_|MID_street_trunk|Icosphere\.?001$)/; // glTF names drop the dot
const CROWN = new THREE.MeshStandardMaterial({ color: '#6b6a3c', roughness: .95 });
function fixMaterials(root) {
  root.traverse(o => {
    if (!o.isMesh) return;
    if (root.name === 'context' && FILLER.test(o.name)) { o.visible = false; o.userData.hidden = true; return; } // float above the exported skirt too
    if (/^Icosphere/.test(o.name)) { o.material = CROWN; return; }
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of mats) {
      if (!m) continue;
      if (m.map) m.map.anisotropy = 4;
      // leaf cards exported without an opacity map would show their white texture background: draw them as solid foliage
      if (/^Leaf_|needle/i.test(m.name) && !(m.alphaTest > 0) && !m.transparent) { m.map = null; m.color.set('#4f5a33'); m.side = THREE.DoubleSide; m.needsUpdate = true; continue; }
      if (m.alphaTest > 0 || (m.transparent && m.map)) { m.alphaTest = 0.45; m.transparent = false; m.side = THREE.DoubleSide; m.userData.leaf = true; }
      else if (m.transparent) { m.depthWrite = false; m.userData.glass = true; }
    }
    o.frustumCulled = true;
  });
}

function clearScene() {
  const mats = new Set();
  campus.traverse(o => { if (o.isMesh) { o.geometry.disposeBoundsTree?.(); o.geometry.dispose(); for (const m of [].concat(o.material)) if (m) mats.add(m); } });
  for (const m of mats) { for (const k of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap', 'alphaMap']) m[k]?.dispose(); m.dispose(); }
  scene.remove(campus); campus = new THREE.Group(); scene.add(campus);
  scene.getObjectByName('ground_far')?.removeFromParent();
  colliders.length = 0; bvhReady = false; loaded = false; look.reset(); trees.reset(); lods.length = 0; gBoxes.length = 0; grassAt = null; grassJob = null; grass.count = 0;
}
let loadToken = 0;
// one unified campus: main, north campus and Sprague/Café Diem share one origin and one manifest
async function loadScene() {
  $('load').hidden = false; $('error').hidden = true;
  const token = ++loadToken;
  clearScene();
  try {
    const base = './models/main/';
    const man = await (await fetch(base + 'manifest.json', { cache: 'no-cache' })).json();
    if (token !== loadToken) return; // a newer load (retry) won
    hasSkirt = man.tiles.some(t => t.file === 'skirt.glb');
    look.setPaint(man.paint || [], base);
    $('source-snapshot').textContent = `Source snapshot: model saved ${man.source_saved}${man.source_version ? ' (' + man.source_version + ')' : ''}; browser export ${man.exported}. Later modeling changes may not appear here yet.`;
    $('footnote').firstChild.textContent = `Working model · ${man.source_saved.replace(/, \d{4},.*/, '')} snapshot · Map data © `;
    // main ground the north merge superseded (e.g. a DTM feather lying across a north sports field), from make_chunks
    const hide = new Set(man.hide || []);
    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    let done = 0, bytes = 0; const total = man.total_bytes || 1, t0 = performance.now();
    // far-field ground and context first, then tiles nearest the view target, a few in parallel
    const tgt = MAIN_CORE.getCenter(new THREE.Vector3());
    const dist = t => t.center ? Math.hypot(t.center[0] - tgt.x, t.center[1] - tgt.z) : -1;
    const queue = [...man.tiles].sort((a, b) => dist(a) - dist(b));
    const loadOne = async t => {
      const g = await loader.loadAsync(base + t.file);
      if (token !== loadToken) return;
      g.scene.name = t.file.replace('.glb', '');
      if (hide.size) { const drop = []; g.scene.traverse(o => { if (o.isMesh && hide.has(o.name)) drop.push(o); }); for (const o of drop) { o.removeFromParent(); o.geometry.dispose(); } }
      fixMaterials(g.scene); liftSportSurfaces(g.scene); look.decorate(g.scene); campus.add(g.scene);
      if (t.file === 'far_houses.glb') g.scene.traverse(o => { if (o.material) { o.material.envMapIntensity = 0.25; o.material.roughness = 0.95; } });
      if (t.file === 'skirt.glb' && man.landcover) applyLandcover(g.scene, base + man.landcover.file, man.landcover.half);
      done++; bytes += t.bytes;
      $('load-text').textContent = `Loading campus… ${Math.round(bytes / total * 100)}% (${done}/${man.tiles.length} tiles)`;
      if (done === 1) overview();
    };
    await loadOne(queue.shift());
    const workers = Array.from({ length: 4 }, async () => { while (queue.length) await loadOne(queue.shift()); });
    await Promise.all(workers);
    if (token !== loadToken) return;
    core.copy(MAIN_CORE);
    // without the real-elevation skirt tile, a simplified distant ground keeps the campus from floating
    if (!hasSkirt) {
    const ground = new THREE.Mesh(new THREE.CircleGeometry(9000, 64).rotateX(-Math.PI / 2), new THREE.MeshStandardMaterial({ color: '#8b9070', roughness: 1 }));
    ground.position.set(core.getCenter(new THREE.Vector3()).x, core.min.y + 0.5, core.getCenter(new THREE.Vector3()).z); ground.name = 'ground_far'; ground.receiveShadow = true; scene.add(ground);
    }
    loaded = true; overview();
    loadLods(man, base, loader, token);
    setTimeout(() => { if (token === loadToken) { indexGround(); snapTrees(); trees.add(campus); } }, 50);
    if (man.far_trees) fetch(base + man.far_trees).then(r => r.arrayBuffer()).then(b => { if (token === loadToken) trees.addFar(new Float32Array(b)); }).catch(e => console.warn('far trees', e));
    window.__campusLoad = { ms: Math.round(performance.now() - t0), tiles: done, bytes };
    $('load').hidden = true;
  } catch (e) {
    console.error(e); $('load').hidden = true; $('error').hidden = false; $('error-text').textContent = String(e.message || e);
  }
}

function overview() {
  setMode('orbit');
  const c = core.getCenter(new THREE.Vector3()), s = core.getSize(new THREE.Vector3());
  const r = Math.max(s.x, s.z) * 0.55;
  controls.target.set(c.x, core.min.y + 25, c.z);
  camera.position.set(c.x + r * 0.55, core.min.y + r * 0.62, c.z + r * 0.85);
  camera.near = 0.5; camera.updateProjectionMatrix(); controls.update();
}
function topView() {
  setMode('orbit');
  const c = core.getCenter(new THREE.Vector3()), s = core.getSize(new THREE.Vector3());
  controls.target.set(c.x, core.min.y, c.z);
  camera.position.set(c.x, core.min.y + Math.max(s.x, s.z) * 1.05, c.z + 0.01); controls.update();
}

// Far-field land cover (from OpenStreetMap, see tools/web-export/landcover.py) draped over the 4 km skirt
function applyLandcover(root, url, half) {
  const tex = new THREE.TextureLoader().load(url);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.flipY = false;
  root.traverse(o => {
    if (!o.isMesh || !/skirt/i.test(o.name + (o.parent?.name || ''))) return;
    o.updateMatrixWorld(true);
    const p = o.geometry.attributes.position, v = new THREE.Vector3(), uv = new Float32Array(p.count * 2);
    for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld); uv[i * 2] = (v.x + half) / (2 * half); uv[i * 2 + 1] = (v.z + half) / (2 * half); }
    o.geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
    // lifted to the campus lawn's brightness so the modelled ground doesn't end in a hard tonal edge
    o.material = new THREE.MeshStandardMaterial({ map: tex, color: new THREE.Color(1.35, 1.35, 1.28), roughness: 0.95, envMapIntensity: 0.3 });
  });
}

// Sports surfaces (turf, courts) are modelled at the same level as the terrain under them, which z-fights
// into a blotchy half-field from a distance. Pull them (and their line markings) forward in depth.
const SPORT_RE = /turf|court|track_surface|pitch_surface/i, LINES_RE = /lines|markings/i;
function liftSportSurfaces(root) {
  const surf = [], lines = [];
  root.traverse(o => { if (!o.isMesh) return; if (SPORT_RE.test(o.name)) surf.push(o); else if (LINES_RE.test(o.name)) lines.push(o); });
  if (!surf.length) return;
  const lift = (o, k) => { o.material = [].concat(o.material).map(m => { const c = m.clone(); c.polygonOffset = true; c.polygonOffsetFactor = -k; c.polygonOffsetUnits = -k; return c; }); if (o.material.length === 1) o.material = o.material[0]; };
  for (const o of surf) lift(o, 1);
  for (const o of lines) lift(o, 2);
}
// ---------------- far tile versions (LOD) ----------------
// Each campus tile can ship a far version (lod/<tile>.glb from tools/web-export/lod.mjs: no instances or
// small parts or interiors, ~0.5 m error, no tears). Past a quality-set distance from the tile's box, the full tile's plain meshes
// move to layer 2 (not rendered, no shadows) and the far version takes layer 0. Instances (trees) stay
// with the full tile: trees.js already culls and swaps those per instance.
const LOD_DIST = { low: 260, medium: 420, high: 650 };
const lods = []; let lodLast = 0;
async function loadLods(man, base, loader, token) {
  const hide = new Set(man.hide || []);
  for (const t of man.tiles) {
    if (!t.lod) continue;
    const full = campus.getObjectByName(t.file.replace('.glb', ''));
    if (!full) continue;
    let g;
    try { g = await loader.loadAsync(base + t.lod); } catch (e) { console.warn('lod', t.lod, e); continue; }
    if (token !== loadToken) return;
    // the far version carries the same objects as the full tile, so drop the ones the merge hides (manifest hide list)
    if (hide.size) { const drop = []; g.scene.traverse(o => { if (o.isMesh && hide.has(o.name)) drop.push(o); }); for (const o of drop) { o.removeFromParent(); o.geometry.dispose(); } }
    g.scene.name = 'lod_' + full.name; fixMaterials(g.scene); liftSportSurfaces(g.scene); look.decorate(g.scene);
    const hi = []; full.traverse(o => { if (o.isMesh && !o.isInstancedMesh && !o.userData.treeLod) hi.push(o); });
    g.scene.traverse(o => { if (o.isMesh) { o.userData.hidden = true; o.userData.lod = true; o.layers.set(2); } });
    campus.add(g.scene);
    lods.push({ hi, lo: g.scene, box: new THREE.Box3().setFromObject(full), far: false });
  }
  updateLods(true);
}
function updateLods(force) {
  const now = performance.now(); if (!force && now - lodLast < 250) return; lodLast = now;
  const D = LOD_DIST[look.quality] || LOD_DIST.medium, p = camera.position;
  for (const l of lods) {
    const far = l.box.distanceToPoint(p) > D;
    if (far === l.far) continue;
    l.far = far;
    for (const o of l.hi) o.layers.set(far ? 2 : 0);
    l.lo.traverse(o => { if (o.isMesh) o.layers.set(far ? 0 : 2); });
  }
}
// ---------------- ground queries (lazy BVH per mesh) ----------------
const gBoxes = []; const DOWN = new THREE.Vector3(0, -1, 0); const gRay = new THREE.Raycaster(); gRay.firstHitOnly = true; gRay.layers.enableAll(); // full tiles' far-swapped meshes sit on layer 2
function indexGround() {
  gBoxes.length = 0; const sz = new THREE.Vector3();
  campus.traverse(o => {
    if (!o.isMesh || o.isInstancedMesh || o.userData.hidden) return;
    const m = [].concat(o.material)[0]; if (m?.userData.leaf || m?.userData.glass) return;
    const b = new THREE.Box3().setFromObject(o); b.getSize(sz);
    gBoxes.push({ o, b, big: Math.max(sz.x, sz.z) > 15 && sz.y < 150 });
  });
}
function topHit(x, z, yTop, bigOnly, boxes = gBoxes) {
  const c = [];
  for (const g of boxes) {
    if ((bigOnly && !g.big) || x < g.b.min.x || x > g.b.max.x || z < g.b.min.z || z > g.b.max.z || g.b.min.y > yTop) continue;
    if (!g.o.geometry.boundsTree) g.o.geometry.computeBoundsTree();
    c.push(g.o);
  }
  if (!c.length) return null;
  gRay.set(new THREE.Vector3(x, yTop, z), DOWN); gRay.far = 800;
  return gRay.intersectObjects(c, false)[0] || null;
}
// Instanced trees whose trunk base hangs over the ground, e.g. edge street trees placed for the
// Blender far-field geometry: lower them onto the ground below. Only ever lowers, 0.8–25 m gaps.
// The base is the lowest point of the tree's geometry (quantized GLBs don't put the origin there).
function snapTrees() {
  const groups = new Map(); const m4 = new THREE.Matrix4(), p = new THREE.Vector3(); let moved = 0;
  campus.traverse(o => { if (o.isInstancedMesh && /^(Tree_|T_)/.test(o.name)) { if (!groups.has(o.parent)) groups.set(o.parent, []); groups.get(o.parent).push(o); } });
  for (const list of groups.values()) {
    const a = list[0]; const sy = new THREE.Vector3().setFromMatrixScale(a.matrixWorld).y || 1;
    let minY = Infinity;
    for (const o of list) { if (!o.geometry.boundingBox) o.geometry.computeBoundingBox(); minY = Math.min(minY, o.geometry.boundingBox.min.y); }
    if (!isFinite(minY)) continue;
    for (let i = 0; i < a.count; i++) {
      a.getMatrixAt(i, m4); p.set(0, minY, 0).applyMatrix4(m4).applyMatrix4(a.matrixWorld);
      const h = topHit(p.x, p.z, p.y + 40, true); if (!h) continue;
      const gap = p.y - h.point.y;
      if (gap > 0.8 && gap < 25) { for (const o of list) { o.getMatrixAt(i, m4); m4.elements[13] -= gap / sy; o.setMatrixAt(i, m4); o.instanceMatrix.needsUpdate = true; } moved++; }
    }
    for (const o of list) o.computeBoundingSphere();
  }
  window.__campusSnapped = moved;
}
// Grass tufts near the camera on lawn surfaces (Medium/High), re-scattered as you move
const GRASS_N = 6000, GRASS_R = 18;
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
// Scattering is spread over frames (up to 7 ms each) and only queries ground meshes near the camera.
let grassAt = null, grassT = 0, grassJob = null;
function updateGrass() {
  if (grassJob) { grassStep(); return; }
  const now = performance.now(); if (now - grassT < 400 || !loaded || !gBoxes.length) return; grassT = now;
  if (look.quality === 'low') { grass.visible = false; return; }
  const c = camera.position; const h = topHit(c.x, c.z, c.y + 2, false);
  if (!h || c.y - h.point.y > 14) { grass.visible = false; return; }
  grass.visible = true;
  if (grassAt && Math.hypot(c.x - grassAt.x, c.z - grassAt.z) < 5) return;
  grassAt = c.clone();
  const yTop = h.point.y + 25, R = GRASS_R;
  const boxes = gBoxes.filter(g => g.b.max.x > c.x - R && g.b.min.x < c.x + R && g.b.max.z > c.z - R && g.b.min.z < c.z + R && g.b.min.y < yTop);
  grassJob = { c: c.clone(), yTop, boxes, i: 0, n: 0 };
  grassStep();
}
const _gm4 = new THREE.Matrix4(), _gq = new THREE.Quaternion(), _gs = new THREE.Vector3(), _gcol = new THREE.Color();
function grassStep() {
  const j = grassJob, t0 = performance.now();
  while (j.i < GRASS_N * 1.6 && j.n < GRASS_N && performance.now() - t0 < 7) {
    j.i++;
    const r = GRASS_R * Math.sqrt(Math.random()), a = Math.random() * Math.PI * 2;
    const x = j.c.x + Math.cos(a) * r, z = j.c.z + Math.sin(a) * r;
    const hit = topHit(x, z, j.yTop, false, j.boxes);
    const m = hit && [].concat(hit.object.material)[0];
    if (!m || m.userData.tp !== 'grass' || !hit.face || hit.face.normal.y < 0.7) continue;
    _gq.setFromAxisAngle(DOWN, Math.random() * Math.PI * 2); const k = 0.7 + Math.random() * 0.8; _gs.set(k, k * (0.8 + Math.random() * 0.5), k);
    _gm4.compose(hit.point, _gq, _gs); grass.setMatrixAt(j.n, _gm4);
    _gcol.copy(m.color).multiplyScalar(1.5 + Math.random() * 0.6); grass.setColorAt(j.n, _gcol); j.n++;
  }
  grass.count = Math.max(grass.count, j.n); grass.instanceMatrix.needsUpdate = true; if (grass.instanceColor) grass.instanceColor.needsUpdate = true;
  if (j.i >= GRASS_N * 1.6 || j.n >= GRASS_N) { grass.count = j.n; grassJob = null; }
}

// ---------------- fly / walk ----------------
const keys = new Set(); let yaw = 0, pitch = 0, locked = false;
const vel = new THREE.Vector3(); let onGround = false;
const player = new THREE.Vector3(); const EYE = 1.65, RADIUS = 0.35;
const avatar = new THREE.Group();
{ const mat = new THREE.MeshStandardMaterial({ color: '#b3282d', roughness: .6 });
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.28, 1.0, 4, 10), mat); body.position.y = 0.8; avatar.add(body);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12), new THREE.MeshStandardMaterial({ color: '#e8c9a8' })); head.position.y = 1.62; avatar.add(head); }
avatar.visible = false; scene.add(avatar);
const crosshair = document.createElement('div'); crosshair.id = 'crosshair'; crosshair.hidden = true; document.body.appendChild(crosshair);

addEventListener('keydown', e => { if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return; keys.add(e.code); if (e.code === 'Space' && mode === 'walk') { jump(); e.preventDefault(); } });
addEventListener('keyup', e => keys.delete(e.code));
canvas.addEventListener('click', () => { if (mode !== 'orbit' && !locked) canvas.requestPointerLock?.(); });
document.addEventListener('pointerlockchange', () => { locked = document.pointerLockElement === canvas; crosshair.hidden = !(locked && mode !== 'orbit'); });
let dragging = false, lx = 0, ly = 0;
canvas.addEventListener('pointerdown', e => { if (mode !== 'orbit' && !locked) { dragging = true; lx = e.clientX; ly = e.clientY; } });
addEventListener('pointerup', () => dragging = false);
addEventListener('pointermove', e => {
  if (mode === 'orbit') return;
  let dx = 0, dy = 0;
  if (locked) { dx = e.movementX; dy = e.movementY; } else if (dragging) { dx = e.clientX - lx; dy = e.clientY - ly; lx = e.clientX; ly = e.clientY; } else return;
  yaw -= dx * 0.0022; pitch = THREE.MathUtils.clamp(pitch - dy * 0.0022, -1.45, 1.45);
});

function lookFromCamera() { const d = new THREE.Vector3(); camera.getWorldDirection(d); yaw = Math.atan2(-d.x, -d.z); pitch = Math.asin(THREE.MathUtils.clamp(d.y, -1, 1)); }

function ensureBVH() {
  if (bvhReady) return;
  campus.traverse(o => {
    if (!o.isMesh || o.isInstancedMesh || o.userData.lod) return; // walking always collides with the full tiles
    const m = Array.isArray(o.material) ? o.material[0] : o.material;
    if (m?.userData.leaf || m?.userData.glass) return;
    if (!o.geometry.boundsTree) o.geometry.computeBoundsTree();
    colliders.push(o);
  });
  bvhReady = true;
}
const ray = new THREE.Raycaster(); ray.firstHitOnly = true; ray.layers.enableAll(); // full tiles swapped out for far versions sit on layer 2
function groundAt(x, y, z, up = 1.2, down = 60) {
  ray.set(new THREE.Vector3(x, y + up, z), new THREE.Vector3(0, -1, 0)); ray.far = up + down;
  const h = ray.intersectObjects(colliders, false)[0]; return h ? h.point.y : null;
}
function blocked(from, dir, dist) {
  for (const hgt of [0.45, 1.2]) {
    ray.set(new THREE.Vector3(from.x, from.y + hgt, from.z), dir); ray.far = dist + RADIUS;
    const h = ray.intersectObjects(colliders, false)[0];
    if (h && h.face && Math.abs(h.face.normal.clone().transformDirection(h.object.matrixWorld).y) < 0.6) return true;
  }
  return false;
}
function spawnPoint() {
  // Center of the loaded campus core; find the ground there.
  const c = core.getCenter(new THREE.Vector3());
  const g = groundAt(c.x, core.max.y + 50, c.z, 0, core.max.y - core.min.y + 200);
  return new THREE.Vector3(c.x, (g ?? core.min.y) + 0.05, c.z);
}
function respawn(at) {
  ensureBVH();
  let p = at;
  if (!p) {
    // spawn under the current camera if over the campus, else the core centre
    const g = groundAt(camera.position.x, camera.position.y + 5, camera.position.z, 0, 800);
    p = g !== null ? new THREE.Vector3(camera.position.x, g + 0.05, camera.position.z) : spawnPoint();
  }
  player.copy(p); vel.set(0, 0, 0); onGround = true; $('walk-status').textContent = 'Click the view to look around. WASD to move, Shift to run, Space to jump.';
}
function jump() { if (onGround) { vel.y = 4.6; onGround = false; } }

function setMode(m) {
  if (m === 'walk' && !loaded) return;
  mode = m;
  for (const id of ['orbit', 'fly', 'walk']) { $(id).classList.toggle('active', id === m); $(id).setAttribute('aria-pressed', id === m); }
  $('flight-controls').hidden = m !== 'fly'; $('walk-controls').hidden = m !== 'walk';
  controls.enabled = m === 'orbit';
  $('help').innerHTML = m === 'orbit' ? 'Drag to orbit · Scroll to zoom<br>Right-drag to pan'
    : m === 'fly' ? 'Click the view to look (Esc to release)<br>WASD move · Q/E down/up · Shift faster' : 'Click the view to look (Esc to release)<br>WASD walk · Shift run · Space jump';
  avatar.visible = m === 'walk' && view === 'third';
  if (m !== 'orbit') { lookFromCamera(); camera.near = m === 'walk' ? 0.1 : 0.3; camera.updateProjectionMatrix(); }
  else { if (document.pointerLockElement) document.exitPointerLock(); camera.near = 0.5; camera.updateProjectionMatrix(); }
  if (m === 'walk') { $('walk-status').textContent = 'Preparing walk mode…'; setTimeout(() => respawn(), 30); }
  crosshair.hidden = !(locked && m !== 'orbit');
}
function setView(v) { view = v; $('view-first').classList.toggle('active', v === 'first'); $('view-third').classList.toggle('active', v === 'third');
  $('view-first').setAttribute('aria-pressed', v === 'first'); $('view-third').setAttribute('aria-pressed', v === 'third'); avatar.visible = mode === 'walk' && v === 'third'; }

const clock = new THREE.Clock(); let frames = 0, acc = 0;
function step(dt) {
  if (mode === 'orbit') { controls.update(); return; }
  const fwd = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw)), right = new THREE.Vector3(-fwd.z, 0, fwd.x);
  const move = new THREE.Vector3();
  if (keys.has('KeyW') || keys.has('ArrowUp')) move.add(fwd); if (keys.has('KeyS') || keys.has('ArrowDown')) move.sub(fwd);
  if (keys.has('KeyD') || keys.has('ArrowRight')) move.add(right); if (keys.has('KeyA') || keys.has('ArrowLeft')) move.sub(right);
  const look = new THREE.Vector3(Math.cos(pitch) * fwd.x, Math.sin(pitch), Math.cos(pitch) * fwd.z);
  if (mode === 'fly') {
    const sp = +$('speed').value * (keys.has('ShiftLeft') || keys.has('ShiftRight') ? 3 : 1);
    const v = new THREE.Vector3();
    if (keys.has('KeyW') || keys.has('ArrowUp')) v.add(look); if (keys.has('KeyS') || keys.has('ArrowDown')) v.sub(look);
    if (keys.has('KeyD') || keys.has('ArrowRight')) v.add(right); if (keys.has('KeyA') || keys.has('ArrowLeft')) v.sub(right);
    if (keys.has('KeyE')) v.y += 1; if (keys.has('KeyQ')) v.y -= 1;
    if (v.lengthSq()) camera.position.addScaledVector(v.normalize(), sp * dt);
    camera.lookAt(camera.position.clone().add(look)); return;
  }
  // walk
  if (!bvhReady) return;
  const speed = (keys.has('ShiftLeft') || keys.has('ShiftRight')) ? 6.5 : 2.6;
  if (move.lengthSq()) {
    move.normalize(); const d = speed * dt;
    // try full move, then axis-separated slides
    for (const m of [move, new THREE.Vector3(move.x, 0, 0), new THREE.Vector3(0, 0, move.z)]) {
      if (!m.lengthSq()) continue; const dir = m.clone().normalize();
      if (blocked(player, dir, d)) continue;
      const nx = player.x + dir.x * d, nz = player.z + dir.z * d;
      const g = groundAt(nx, player.y, nz, 0.45, 3);
      if (g === null && onGround) continue;           // don't walk off into the void
      player.x = nx; player.z = nz; break;
    }
  }
  vel.y -= 9.81 * dt; player.y += vel.y * dt;
  const g = groundAt(player.x, player.y, player.z, 0.5, 2);
  if (g !== null && player.y <= g + 0.02) { player.y = g; vel.y = 0; onGround = true; } else onGround = false;
  if (player.y < core.min.y - 50) respawn(spawnPoint());
  if (view === 'first') { camera.position.set(player.x, player.y + EYE, player.z); camera.lookAt(camera.position.clone().add(look)); }
  else {
    avatar.position.copy(player); avatar.rotation.y = yaw;
    const back = look.clone().multiplyScalar(-4.5); const eye = player.clone().add(new THREE.Vector3(0, 1.9, 0)).add(back);
    camera.position.copy(eye); camera.lookAt(player.clone().add(new THREE.Vector3(0, 1.4, 0)));
  }
}
function loop() {
  const dt = Math.min(clock.getDelta(), 0.1); step(dt); look.update(mode === 'orbit' ? controls.target : null); trees.update(); updateLods(); updateGrass(); look.render();
  frames++; acc += dt; if (acc > 1) { $('performance').textContent = `${Math.round(frames / acc)} fps · ${(renderer.info.render.triangles / 1e6).toFixed(1)} M triangles`; frames = 0; acc = 0; }
  requestAnimationFrame(loop);
}
loop();

$('orbit').onclick = () => setMode('orbit'); $('fly').onclick = () => setMode('fly'); $('walk').onclick = () => setMode('walk');
$('reset').onclick = overview; $('top').onclick = topView; $('jump').onclick = jump; $('respawn').onclick = () => respawn(spawnPoint());
$('view-first').onclick = () => setView('first'); $('view-third').onclick = () => setView('third');
$('speed').oninput = () => $('speed-label').textContent = $('speed').value + ' m/s';
const savedQ = localStorage.getItem('campus-quality');
$('quality').value = ['low', 'medium', 'high'].includes(savedQ) ? savedQ : 'medium';
const setQuality = v => { look.applyQuality(v); trees.setQuality(v); lodLast = 0; localStorage.setItem('campus-quality', v); resize(); };
$('quality').onchange = e => setQuality(e.target.value);
setQuality(new URLSearchParams(location.search).get('quality') || $('quality').value);
$('retry').onclick = () => loadScene();
// test hook for headless screenshots: window.__campus.goto(x,y,z, tx,ty,tz)
window.__campusScene = scene;
window.__campus = { THREE, camera, controls, setMode, topView, overview, look, trees, setQuality, loadScene, get loaded() { return loaded; }, get lods() { return lods.length; },
  goto(x, y, z, tx, ty, tz) { setMode('orbit'); camera.position.set(x, y, z); controls.target.set(tx, ty, tz); controls.update(); },
  groundAt: (x, z) => { ensureBVH(); return groundAt(x, 400, z, 0, 600); } };
loadScene();
