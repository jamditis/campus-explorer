// Montclair State campus · working model — static three.js viewer (no build step).
// Tiles: ./models/main/manifest.json lists GLB tiles (meshopt-compressed, webp textures).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from 'three-mesh-bvh';
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;

const $ = id => document.getElementById(id);
const canvas = $('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: new URLSearchParams(location.search).has('capture') });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.95;
renderer.setPixelRatio(1);
const scene = new THREE.Scene();
const SKY = new THREE.Color('#c9d6e2');
scene.background = SKY; scene.fog = new THREE.Fog(SKY, 900, 4200);
const camera = new THREE.PerspectiveCamera(50, 1, 0.3, 20000);
scene.add(new THREE.HemisphereLight('#e6eefa', '#5f5a48', 0.85));
const sun = new THREE.DirectionalLight('#fff1da', 1.7); sun.position.set(-400, 700, 300); scene.add(sun);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.08; controls.maxPolarAngle = Math.PI * 0.495;
controls.minDistance = 3; controls.maxDistance = 6000; controls.screenSpacePanning = false;

let campus = new THREE.Group(); scene.add(campus);
let core = new THREE.Box3(new THREE.Vector3(-420, 95, -300), new THREE.Vector3(330, 150, 420)), loaded = false, mode = 'orbit', view = 'first';
const colliders = []; let bvhReady = false;

function resize() { const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
addEventListener('resize', resize); resize();

// far-field filler crowns/trunks were built to sit on the Blender far-field skirt, which the browser edition drops
const FILLER = /^(WS62_crown_|MID_street_trunk|Icosphere\.001$)/;
const CROWN = new THREE.MeshStandardMaterial({ color: '#6b6a3c', roughness: .95 });
function fixMaterials(root) {
  root.traverse(o => {
    if (!o.isMesh) return;
    if (root.name === 'context' && FILLER.test(o.name)) { o.visible = false; return; }
    if (/^Icosphere/.test(o.name)) { o.material = CROWN; return; }
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    for (const m of mats) {
      if (!m) continue;
      if (m.map) m.map.anisotropy = 4;
      if (m.alphaTest > 0 || (m.transparent && m.map)) { m.alphaTest = 0.45; m.transparent = false; m.side = THREE.DoubleSide; m.userData.leaf = true; }
      else if (m.transparent) { m.depthWrite = false; m.userData.glass = true; }
    }
    o.frustumCulled = true;
  });
}

async function loadScene(tile) {
  $('load').hidden = false; $('error').hidden = true;
  try {
    const base = `./models/${tile}/`;
    const man = await (await fetch(base + 'manifest.json', { cache: 'no-cache' })).json();
    $('source-snapshot').textContent = `Source snapshot: model saved ${man.source_saved}${man.source_version ? ' (' + man.source_version + ')' : ''}; browser export ${man.exported}. Later modeling changes may not appear here yet.`;
    $('footnote').firstChild.textContent = `Working model · ${man.source_saved.replace(/, \d{4},.*/, '')} snapshot · Map data © `;
    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    let done = 0, bytes = 0; const total = man.total_bytes || 1, t0 = performance.now();
    const coreBox = new THREE.Box3();
    // context first (terrain + surroundings), then the tiles, a few in parallel
    const queue = [...man.tiles];
    const loadOne = async t => {
      const g = await loader.loadAsync(base + t.file);
      g.scene.name = t.file.replace('.glb', ''); fixMaterials(g.scene); campus.add(g.scene);
      if (t.file !== 'context.glb') coreBox.expandByObject(g.scene);
      done++; bytes += t.bytes;
      $('load-text').textContent = `Loading campus… ${Math.round(bytes / total * 100)}% (${done}/${man.tiles.length} tiles)`;
      if (done === 1) overview();
    };
    await loadOne(queue.shift());
    const workers = Array.from({ length: 4 }, async () => { while (queue.length) await loadOne(queue.shift()); });
    await Promise.all(workers);
    core.copy(coreBox.isEmpty() ? new THREE.Box3().setFromObject(campus) : coreBox);
    // simplified distant ground so the campus doesn't float in the sky
    const ground = new THREE.Mesh(new THREE.CircleGeometry(9000, 64).rotateX(-Math.PI / 2), new THREE.MeshStandardMaterial({ color: '#8b9070', roughness: 1 }));
    ground.position.set(core.getCenter(new THREE.Vector3()).x, core.min.y + 0.5, core.getCenter(new THREE.Vector3()).z); ground.name = 'ground_far'; scene.add(ground);
    loaded = true; overview();
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
    if (!o.isMesh || o.isInstancedMesh) return;
    const m = Array.isArray(o.material) ? o.material[0] : o.material;
    if (m?.userData.leaf || m?.userData.glass) return;
    if (!o.geometry.boundsTree) o.geometry.computeBoundsTree();
    colliders.push(o);
  });
  bvhReady = true;
}
const ray = new THREE.Raycaster(); ray.firstHitOnly = true;
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
  const dt = Math.min(clock.getDelta(), 0.1); step(dt); renderer.render(scene, camera);
  frames++; acc += dt; if (acc > 1) { $('performance').textContent = `${Math.round(frames / acc)} fps · ${(renderer.info.render.triangles / 1e6).toFixed(1)} M triangles`; frames = 0; acc = 0; }
  requestAnimationFrame(loop);
}
loop();

$('orbit').onclick = () => setMode('orbit'); $('fly').onclick = () => setMode('fly'); $('walk').onclick = () => setMode('walk');
$('reset').onclick = overview; $('top').onclick = topView; $('jump').onclick = jump; $('respawn').onclick = () => respawn(spawnPoint());
$('view-first').onclick = () => setView('first'); $('view-third').onclick = () => setView('third');
$('speed').oninput = () => $('speed-label').textContent = $('speed').value + ' m/s';
$('quality').onchange = e => { renderer.setPixelRatio(e.target.checked ? Math.min(devicePixelRatio, 2) : 1); resize(); };
$('retry').onclick = () => loadScene($('tile').value);
$('tile').onchange = () => loadScene($('tile').value);
// test hook for headless screenshots: window.__campus.goto(x,y,z, tx,ty,tz)
window.__campus = { THREE, camera, controls, setMode, topView, overview, get loaded() { return loaded; },
  goto(x, y, z, tx, ty, tz) { setMode('orbit'); camera.position.set(x, y, z); controls.target.set(tx, ty, tz); controls.update(); },
  groundAt: (x, z) => { ensureBVH(); return groundAt(x, 400, z, 0, 600); } };
loadScene('main');
