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
import { createDoors } from './viewer/doors.js';
import { createCamera } from './viewer/camera.js';
import { createUI } from './viewer/ui.js';
import { CAMPUS, convergenceDeg, gridToTrueBearing } from './viewer/geo.js';
import { sunPosition, zonedDate } from './viewer/sun.js';
import { parseRooms, roomPlaces, walkStartY } from './viewer/rooms-math.js';
import { landPose } from './viewer/pose-math.js';
import { flightLimit, clampToLimit } from './viewer/flight-math.js';
import { southWestOffset } from './viewer/labels-math.js';

const params = new URLSearchParams(location.search);
const canvas = document.getElementById('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', preserveDrawingBuffer: params.has('capture') });
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.5, 33000);
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
  places: [], home: null, limit: null, rooms: { volumes: [], rooms: [] }, roomPlaces: [],
  time: { date: zonedDate(DEFAULT_TIME), preset: true },
  on(type, fn) { (listeners.get(type) ?? listeners.set(type, new Set()).get(type)).add(fn); return () => app.off(type, fn); },
  off(type, fn) { listeners.get(type)?.delete(fn); },
  emit(type, detail) { const set = listeners.get(type); if (set) for (const fn of set) fn(detail); },
  /**
   * Ask for a redraw. `lazy` is for changes that can wait a moment (a tile arrived while the view is still):
   * on a GPU that needs more than SLOW_FRAME_MS per frame the redraw is put off for a few frame times, so
   * that drawing each arriving tile does not hold up the tiles behind it.
   */
  invalidate(lazy = false) {
    if (lazy && frameMs > SLOW_FRAME_MS) lazyAt ||= performance.now() + Math.min(LAZY_MAX_MS, frameMs * 6);
    else dirty = Math.max(dirty, 2);
  },
  focus(out = new THREE.Vector3()) { return out.copy(app.state.mode === 'orbit' ? controls.target : app.state.mode === 'walk' ? app.player.focus : camera.position); },
  heading() { camera.getWorldDirection(_v); return gridToTrueBearing(THREE.MathUtils.radToDeg(Math.atan2(_v.x, -_v.z)), CAMPUS.lat, CAMPUS.lon); },
  isIdle: () => performance.now() - lastMove > 400,
  toast(text) { app.emit('toast', { text }); },
};
const _v = new THREE.Vector3();
let dirty = 2, lastMove = 0;
const SLOW_FRAME_MS = 80, LAZY_MAX_MS = 20000;
let frameMs = 16, lazyAt = 0, drew = false; // smoothed time of a drawn frame; when a lazy redraw is due

app.look = createLook(renderer, scene, camera, () => app.invalidate());
const scenery = createScenery(app);
app.world = createWorld(app, scenery.prepare, root => { scenery.release(root); app.look.forget(root); app.doors.forget(root); });
app.input = createInput(canvas, document.getElementById('overlay'));
app.player = createPlayer(app);
app.doors = createDoors(app); // entrance doors that open in walk mode
const cam = createCamera(app);
/** Ease the camera to a pose. `by` names the module that asked, so others can tell their own moves from a new one. */
/**
 * `land: true` (moves to a place): once the move arrives and the tiles there are in, put the target on the
 * real ground and keep the camera above the ground or roof under it (viewer/pose-math.js landPose).
 * `app.landing` is the promise of that last step while it runs.
 */
app.flyTo = (pose, opts = {}) => {
  app.emit('fly', { by: opts.by ?? null });
  const moved = cam.flyTo(pose, opts);
  if (!opts.land) return moved;
  return moved.then(done => { if (done) { const my = landSeq; app.landing = land(my).finally(() => { if (my === landSeq) app.landing = null; }); } return done; });
};
let landSeq = 0;
app.on('fly', () => { landSeq++; });
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function land(my) {
  const t = controls.target, c = camera.position, w = app.world;
  // the lookup before the move may have hit nothing (tiles still streaming) or only the far-field skirt
  while (!w.isLoaded(t.x, t.z) || !w.isLoaded(c.x, c.z)) {
    w.prioritize(t.x, t.z); w.prioritize(c.x, c.z);
    await sleep(250); if (my !== landSeq) return;
  }
  await w.warm(t.x, t.z, 2); await w.warm(c.x, c.z, 2);
  if (my !== landSeq || app.state.mode !== 'orbit') return;
  const next = landPose({ position: c, target: t }, w.groundAt(t.x, t.z), w.groundAt(c.x, c.z));
  if (!next) return;
  c.set(next.position.x, next.position.y, next.position.z); t.set(next.target.x, next.target.y, next.target.z);
  controls.update(); app.invalidate();
}
/** Stop any camera move without touching the pose, for modules that place the camera themselves. */
app.cancelFly = (by = null) => { app.emit('fly', { by }); cam.cancel(); };
/** Draw the whole campus with another camera into `target` (the minimap). The main view's tree and size culling is undone for the picture. */
app.renderPlain = (camera2, target) => { scenery.trees.showAll(); app.look.renderPlain(camera2, target); scenery.trees.update(true); };

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
  if (place.kind === 'room') return goToRoom(place, opts);
  app.world.prioritize(place.x, place.z); app.emit('place', { place });
  return app.flyTo(app.placePose(place), { ...opts, land: true });
};
/**
 * Where a move to a place ends: looking at its ground from 70 m or more, along the current heading, or
 * from the south-west (`southwest`, the tour). The ground is a first guess (collision that is already
 * built, else the full lookup where the tiles are in, else the campus floor); `land` corrects it on arrival.
 */
app.placePose = (place, from = 'heading') => {
  const w = app.world, floor = isFinite(app.bounds.min.y) ? app.bounds.min.y + 20 : 130;
  const y = w.groundAt(place.x, place.z, null, { builtOnly: true }) ?? (w.isLoaded(place.x, place.z) ? w.groundAt(place.x, place.z) : null) ?? floor;
  const target = new THREE.Vector3(place.x, y, place.z);
  if (from === 'southwest') { const o = southWestOffset(place.r); return { target, position: target.clone().add(new THREE.Vector3(o.dx, o.dy, o.dz)) }; }
  const dist = Math.max(70, (place.r || 20) * 2.4);
  camera.getWorldDirection(_v); _v.y = 0; if (_v.lengthSq() < 1e-4) _v.set(0, 0, -1);
  const position = target.clone().addScaledVector(_v.normalize(), -dist * 0.8); position.y += dist * 0.6;
  return { position, target };
};
/** A room (viewer/rooms.json): glide to eye height on its floor, then stand there in walk mode. */
async function goToRoom(room, opts) {
  const at = new THREE.Vector3(room.x, room.y, room.z), eye = at.clone().setY(room.y + 1.65);
  camera.getWorldDirection(_v); _v.y = 0; if (_v.lengthSq() < 1e-4) _v.set(0, 0, -1); _v.normalize();
  app.world.prioritize(room.x, room.z); app.emit('place', { place: room });
  // the target sits a little low: orbit controls do not look up
  const ok = await app.flyTo({ position: eye, target: eye.clone().addScaledVector(_v, 4).setY(eye.y - 0.3) }, opts);
  if (ok) await app.setMode('walk', { at });
  return ok;
}
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
    // the storey under the camera, not the roof above it (walkStartY): from fly mode inside a building too
    if (await app.player.teleport(spot.x, spot.z, at ? spot.y : walkStartY(from, spot.y)) === false) await app.player.respawn();
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
  setLimit();
  app.look.setPaint(manifest.paint || [], base);
  try { app.places = (await (await fetch('./viewer/places.json')).json()).places.filter(p => app.world.tileAt(p.x, p.z)); } catch { app.places = []; }
  // buildings with a real interior and their room numbers (?interiors=0 leaves the rule out, for comparison)
  try { app.rooms = params.get('interiors') === '0' ? parseRooms(null) : parseRooms(await (await fetch('./viewer/rooms.json')).json()); } catch { app.rooms = parseRooms(null); }
  app.roomPlaces = roomPlaces(app.rooms);
  app.look.setInteriors(app.rooms.volumes);
  app.emit('places');
});
app.on('scene:ready', () => {
  app.state.ready = true; setLimit();
  // the lite profile has no terrain skirt: a flat disc keeps the campus from floating
  if (app.lite) { const c = app.bounds.getCenter(_v); app.look.setFarGround(true, c.x, (isFinite(app.bounds.min.y) ? app.bounds.min.y : 110) - 6, c.z); }
});
app.on('scene:complete', () => { app.state.complete = true; setLimit(); });
// the soft flight limit (viewer/flight-math.js): from the manifest's tiles and skirt, the ceiling over the campus floor
function setLimit() {
  const m = app.manifest; if (!m) return;
  app.limit = flightLimit(m.tiles, { skirtHalf: m.landcover?.half ?? 2000, floorY: isFinite(app.bounds.min.y) ? app.bounds.min.y : 100 });
}
// hard stop for everything that is not eased at the limit: orbit zoom and pan, eased moves, share links
function clampView() {
  if (!app.limit) return;
  camera.position.copy(clampToLimit(camera.position, app.limit));
  if (app.state.mode === 'orbit') controls.target.copy(clampToLimit(controls.target, app.limit));
}

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
  if (drew) frameMs += (Math.min(now - last, 5000) - frameMs) * 0.3; // the frame after a draw arrives late on a slow GPU
  drew = false;
  const dt = Math.min((now - last) / 1000, 0.1); last = now;
  if (lazyAt && now >= lazyAt) { dirty = Math.max(dirty, 2); lazyAt = 0; }
  const mode = app.state.mode;
  app.emit('frame', { dt, time: now });
  if (mode === 'orbit') controls.update(); else app.player.step(dt, app.input.update(dt));
  clampView();
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
    drew = true; lazyAt = 0; // this draw shows whatever a lazy request was waiting for
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
