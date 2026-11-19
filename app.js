// Montclair State campus · working model — static three.js viewer (no build step).
// Entry point: builds the renderer and the shared `app` object, runs the frame loop and wires the
// modules in viewer/. The contract between modules is in docs/VIEWER.md.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createLook } from './look.js';
import { createWorld } from './viewer/world.js';
import { createScenery } from './viewer/scenery.js';
import { createInput } from './viewer/input.js';
import { createPlayer } from './viewer/player.js';
import { createCamera } from './viewer/camera.js';
import { createUI } from './viewer/ui.js';
import { CAMPUS, convergenceDeg, gridToTrueBearing } from './viewer/geo.js';
import { sunPosition, zonedDate } from './viewer/sun.js';

const params = new URLSearchParams(location.search);
const canvas = document.getElementById('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: params.has('capture') });
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.5, 20000);
camera.position.set(180, 480, 420);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.08; controls.maxPolarAngle = Math.PI * 0.495;
controls.minDistance = 3; controls.maxDistance = 6000; controls.screenSpacePanning = false;
controls.target.set(-80, 130, -160);

// ---- the shared app object ----
const listeners = new Map();
const FOV = { orbit: 50, fly: 60, walk: 68 };
const LITE_TILES = 9; // centred tiles kept in memory in the lite profile
// Default light: a real afternoon. 22 September 2026, 2:45 pm in Montclair puts the sun in the south-west, about 41° up.
const DEFAULT_TIME = { year: 2026, month: 9, day: 22, hour: 14, minute: 45 };
const app = {
  THREE, renderer, scene, camera, canvas, controls,
  state: { mode: 'orbit', view: 'first', ready: false, complete: false },
  bounds: new THREE.Box3(),
  places: [], home: null,
  time: { date: zonedDate(DEFAULT_TIME), preset: true },
  on(type, fn) { (listeners.get(type) ?? listeners.set(type, new Set()).get(type)).add(fn); return () => app.off(type, fn); },
  off(type, fn) { listeners.get(type)?.delete(fn); },
  emit(type, detail) { const set = listeners.get(type); if (set) for (const fn of set) fn(detail); },
  invalidate() { dirty = Math.max(dirty, 2); },
  focus(out = new THREE.Vector3()) { return out.copy(app.state.mode === 'orbit' ? controls.target : app.state.mode === 'walk' ? app.player.focus : camera.position); },
  heading() { camera.getWorldDirection(_v); return gridToTrueBearing(THREE.MathUtils.radToDeg(Math.atan2(_v.x, -_v.z)), CAMPUS.lat, CAMPUS.lon); },
  isIdle: () => performance.now() - lastMove > 400,
  toast(text) { app.emit('toast', { text }); },
};
const _v = new THREE.Vector3();
let dirty = 2, lastMove = 0;

app.look = createLook(renderer, scene, camera, () => app.invalidate());
const scenery = createScenery(app);
app.world = createWorld(app, scenery.prepare, root => { scenery.release(root); app.look.forget(root); });
app.input = createInput(canvas, document.getElementById('overlay'));
app.player = createPlayer(app);
const cam = createCamera(app);
app.flyTo = cam.flyTo;

// ---- sun ----
/** Move the sun to its real position for an instant (a Date). `preset` marks the default light. */
app.setTime = (date, preset = false) => {
  app.time = { date, preset };
  const { azimuth, elevation } = sunPosition(date, CAMPUS.lat, CAMPUS.lon);
  // the model's -Z axis is grid north, which sits a fraction of a degree east of true north
  const bearing = THREE.MathUtils.degToRad(azimuth - convergenceDeg(CAMPUS.lat, CAMPUS.lon)), el = THREE.MathUtils.degToRad(elevation);
  app.look.setSun(_v.set(Math.sin(bearing) * Math.cos(el), Math.sin(el), -Math.cos(bearing) * Math.cos(el)), elevation);
  app.sun = { azimuth, elevation };
  app.emit('sun', { azimuth, elevation, date, preset }); app.invalidate();
};
app.resetTime = () => app.setTime(zonedDate(DEFAULT_TIME), true);

// ---- size and quality ----
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); app.look.resize();
  app.emit('resize', { width: w, height: h }); app.invalidate();
}
addEventListener('resize', resize);
app.setQuality = name => {
  if (!['low', 'medium', 'high'].includes(name)) name = 'medium';
  app.look.applyQuality(name);
  try { localStorage.setItem('campus-quality', name); } catch { /* private mode */ }
  resize(); app.emit('quality', { name });
};

// ---- views ----
function framing() {
  const b = app.bounds, c = b.getCenter(new THREE.Vector3()), s = b.getSize(new THREE.Vector3());
  const floor = isFinite(b.min.y) ? b.min.y : 110;
  return { c, floor, span: Math.max(s.x, s.z) || 800 };
}
app.overviewPose = () => {
  const { c, floor, span } = framing(), r = span * 0.5;
  return { position: new THREE.Vector3(c.x + r * 0.55, floor + r * 0.62, c.z + r * 0.85), target: new THREE.Vector3(c.x, floor + 25, c.z) };
};
app.topPose = () => {
  const { c, floor, span } = framing();
  return { position: new THREE.Vector3(c.x, floor + span * 1.05, c.z + 0.01), target: new THREE.Vector3(c.x, floor, c.z) };
};
/** Fly to a place from places.json, keeping the current heading so the move is easy to follow. */
app.goToPlace = (place, opts) => {
  const floor = isFinite(app.bounds.min.y) ? app.bounds.min.y + 20 : 130;
  const y = app.world.groundAt(place.x, place.z, null, { builtOnly: true }) ?? floor;
  const dist = Math.max(70, (place.r || 20) * 2.4);
  camera.getWorldDirection(_v); _v.y = 0; if (_v.lengthSq() < 1e-4) _v.set(0, 0, -1);
  const target = new THREE.Vector3(place.x, y, place.z);
  const position = target.clone().addScaledVector(_v.normalize(), -dist * 0.8); position.y += dist * 0.6;
  app.world.prioritize(place.x, place.z); app.emit('place', { place });
  return app.flyTo({ position, target }, opts);
};
app.overview = opts => app.flyTo(app.overviewPose(), opts);
app.topView = opts => app.flyTo(app.topPose(), opts);

// ---- modes ----
/** Switch between orbit, fly and walk. Walk drops you where the middle of the view points. */
app.setMode = async (mode, { at = null } = {}) => {
  const from = app.state.mode;
  if (mode === from && !at) return;
  cam.cancel(); app.player.stop();
  if (mode === 'orbit') {
    // keep looking at what was ahead instead of snapping back to the old orbit centre
    camera.getWorldDirection(_v);
    const hit = app.world.raycast(camera.position, _v, 400, { builtOnly: true });
    controls.target.copy(camera.position).addScaledVector(_v, hit ? Math.max(8, hit.distance) : 60);
  } else app.player.lookFromCamera();
  app.state.mode = mode;
  controls.enabled = mode === 'orbit';
  app.input.setEnabled(mode !== 'orbit'); if (mode !== 'orbit') app.input.setMode(mode);
  camera.near = mode === 'walk' ? 0.1 : mode === 'fly' ? 0.3 : 0.5;
  app.player.avatar.visible = mode === 'walk' && app.state.view === 'third';
  app.emit('mode', { mode, view: app.state.view }); app.invalidate();
  if (mode === 'walk') {
    let spot = at;
    if (!spot) {
      const r = canvas.getBoundingClientRect();
      const hit = from === 'orbit' ? app.world.pick(r.left + r.width / 2, r.top + r.height / 2) : null;
      spot = hit ? hit.point : from === 'orbit' ? controls.target : camera.position;
    }
    // false: nothing to stand on there, so start from the middle. null: the user moved on; leave the camera alone.
    if (await app.player.teleport(spot.x, spot.z, at || from === 'orbit' ? spot.y : null) === false) await app.player.respawn();
  }
};
app.setView = view => {
  app.state.view = view; app.player.avatar.visible = app.state.mode === 'walk' && view === 'third';
  app.player.refresh(); app.emit('mode', { mode: app.state.mode, view }); app.invalidate();
};

// ---- the campus ----
/** Load the campus tiles. `view` is a decoded permalink; its target decides which tiles come first. */
app.load = async ({ view = null } = {}) => {
  app.state.ready = app.state.complete = false;
  if (app.state.mode !== 'orbit') await app.setMode('orbit');
  app.look.reset(); app.home = null;
  const limit = Number(params.get('tiles')) || Infinity;
  const saver = navigator.connection?.saveData === true && !params.has('all');
  try {
    await app.world.load({
      limit, stream: !saver, focus: view?.target ? { x: view.target[0], z: view.target[2] } : null,
      budget: app.lite ? LITE_TILES : Infinity, skirt: !app.lite,
    });
  } catch (e) {
    if (e.name === 'AbortError') return;
    console.error(e); app.emit('scene:error', { error: e });
  }
};
app.on('scene:start', async ({ manifest, base }) => {
  app.manifest = manifest;
  app.look.setPaint(manifest.paint || [], base);
  try { app.places = (await (await fetch('./viewer/places.json')).json()).places.filter(p => app.world.tileAt(p.x, p.z)); } catch { app.places = []; }
  app.emit('places');
});
app.on('scene:ready', () => {
  app.state.ready = true;
  // the lite profile has no terrain skirt: a flat disc keeps the campus from floating
  if (app.lite) { const c = app.bounds.getCenter(_v); app.look.setFarGround(true, c.x, (isFinite(app.bounds.min.y) ? app.bounds.min.y : 110) - 6, c.z); }
});
app.on('scene:complete', () => { app.state.complete = true; });

// ---- frame loop: draw only when something changed ----
const lastCam = new Float64Array(18); let moving = false, fov = 50, last = performance.now(), frames = 0, acc = 0;
function cameraChanged() {
  camera.updateMatrixWorld();
  const e = camera.matrixWorld.elements, p = camera.projectionMatrix.elements; let changed = false;
  for (let i = 0; i < 16; i++) if (Math.abs(e[i] - lastCam[i]) > 1e-6) { changed = true; lastCam[i] = e[i]; }
  if (lastCam[16] !== p[0] || lastCam[17] !== p[5]) { changed = true; lastCam[16] = p[0]; lastCam[17] = p[5]; }
  return changed;
}
function loop(now) {
  requestAnimationFrame(loop);
  const dt = Math.min((now - last) / 1000, 0.1); last = now;
  const mode = app.state.mode;
  app.emit('frame', { dt, time: now });
  if (mode === 'orbit') controls.update(); else app.player.step(dt, app.input.update(dt));
  const want = FOV[mode];
  if (Math.abs(fov - want) > 0.05) { fov += (want - fov) * (1 - Math.exp(-dt * 6)); camera.fov = fov; camera.updateProjectionMatrix(); }
  const changed = cameraChanged();
  if (changed) { lastMove = now; app.emit('camera'); }
  const settle = moving && !changed; // the camera just stopped: one sharp frame with fresh culling
  moving = changed;
  if (changed || settle || dirty > 0) {
    app.look.update(mode === 'orbit' ? controls.target : null, settle || dirty > 0);
    app.look.render(changed);
    if (dirty > 0) dirty--;
    frames++; app.emit('drawn');
  }
  acc += dt;
  if (acc >= 1) { app.emit('stats', { fps: Math.round(frames / acc), triangles: renderer.info.render.triangles, scale: app.look.scale }); frames = 0; acc = 0; }
}

// ---- start ----
const saved = (() => { try { return localStorage.getItem('campus-quality'); } catch { return null; } })();
const phone = matchMedia('(pointer: coarse)').matches && Math.min(screen.width, screen.height) < 820;
// Lite profile: a phone tab cannot hold the whole campus. Keep the tiles near the view and skip the 4 km skirt.
// ?lite=1 or ?lite=0 forces it either way.
app.lite = params.has('lite') ? params.get('lite') !== '0' : phone || (navigator.deviceMemory ?? 8) <= 2;
const ui = createUI(app);
app.setQuality(params.get('quality') || saved || (phone ? 'low' : 'medium'));
app.resetTime();
resize();
requestAnimationFrame(loop);
ui.start();

// test hook for headless screenshots and the smoke test
window.__campus = {
  app, THREE, camera, controls,
  get loaded() { return app.state.complete; }, get ready() { return app.state.ready; },
  goto(x, y, z, tx, ty, tz) { if (app.state.mode !== 'orbit') app.setMode('orbit'); cam.cancel(); camera.position.set(x, y, z); controls.target.set(tx, ty, tz); controls.update(); app.invalidate(); },
  groundAt: (x, z) => app.world.groundAt(x, z),
  trees: scenery.trees, get lods() { return app.world.lods; }, get grass() { return scenery.grass; },
};
