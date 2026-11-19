// Heads-up display over the 3D view: compass, scale bar, position readout and a top-down minimap.
// DOM only, except the minimap picture, which is the model itself drawn once from above into a
// render target and kept as a static image until tiles change.
import * as THREE from 'three';
import { CAMPUS, compassPoint, convergenceDeg, formatLatLon, localToLatLon } from './geo.js';
import {
  metresPerPixel, niceScale, formatScale, formatElevation, mapExtent, worldToMap, mapToWorld,
  northOffset, northYaw, horizontalFov, headingLabel, toneMapToSrgb,
} from './hud-math.js';

const MAP_PX = 512;            // render target and picture size; the SVG marks use the same units
const READOUT_MS = 200;        // position and scale update at most 5 times a second
const MAP_GAP_MS = 2000;       // re-render the map picture at most every 2 s while tiles arrive
const KEY_STEP = 20;           // metres per arrow key press on the map
const PAPER = [233, 236, 239]; // map background where the model has nothing
const STORE = 'campus-map';
const CONV = convergenceDeg(CAMPUS.lat, CAMPUS.lon);
const TIP = "Position from the model's New Jersey State Plane frame (EPSG:6527). Elevation from NJ LiDAR as modelled; not a survey.";
const SVG = 'http://www.w3.org/2000/svg';

function el(tag, cls, attrs = {}) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
}
function svg(tag, attrs = {}) {
  const e = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
}
function load() {
  try { return localStorage.getItem(STORE); } catch { return null; }
}
function save(on) {
  try { localStorage.setItem(STORE, on ? '1' : '0'); } catch { /* private mode */ }
}

/**
 * Build the HUD inside #overlay. Returns { setMap(on), map, setVisible(on), dispose() }.
 * Emits `hud:map` { on } whenever the minimap is shown or hidden.
 */
export function createHud(app) {
  const { camera, controls, renderer } = app;
  const overlay = document.getElementById('overlay');

  // ---- DOM ----
  const root = el('div', 'hud');
  const left = el('div', 'hud-left');
  const compass = el('button', 'hud-compass', { type: 'button', 'aria-label': 'Face north', title: 'Face north' });
  const dial = el('span', 'hud-dial', { 'aria-hidden': 'true' });
  dial.innerHTML = '<svg viewBox="-20 -20 40 40" focusable="false"><circle r="18.5" class="hud-dial-ring"/>'
    + '<path d="M0 -18 L4 -11 L-4 -11 Z" class="hud-dial-n"/><path d="M0 17.5 L2.5 13 L-2.5 13 Z" class="hud-dial-s"/>'
    + '<path d="M17.5 0 L13 0 M-17.5 0 L-13 0" class="hud-dial-tick"/>'
    + '<text y="1" class="hud-dial-label">N</text></svg>';
  const bearing = el('span', 'hud-bearing', { 'aria-hidden': 'true' });
  compass.append(dial, bearing);

  const map = el('div', 'hud-map');
  const view = el('div', 'hud-map-view', { role: 'application', tabindex: '0', 'aria-label': 'Campus map. Click to move the view.' });
  const pic = el('canvas', 'hud-map-pic', { width: MAP_PX, height: MAP_PX, 'aria-hidden': 'true' });
  const marks = svg('svg', { class: 'hud-map-marks', viewBox: `0 0 ${MAP_PX} ${MAP_PX}`, 'aria-hidden': 'true' });
  const wedge = svg('path', { class: 'hud-wedge' });
  const dot = svg('circle', { class: 'hud-dot', r: '11' });
  marks.append(wedge, dot);
  view.append(pic, marks);
  const close = el('button', 'hud-map-close', { type: 'button', 'aria-label': 'Hide map', title: 'Hide map' });
  close.textContent = '×';
  map.append(view, close);
  left.append(compass, map);

  const info = el('div', 'hud-info');
  const scale = el('div', 'hud-scale', { 'aria-hidden': 'true' });
  const bar = el('span', 'hud-scale-bar');
  const scaleText = el('span', 'hud-scale-label');
  scale.append(bar, scaleText);
  const readout = el('div', 'hud-readout', { title: TIP });
  const where = el('span', 'hud-where');
  const latlon = el('span', 'hud-latlon');
  const elev = el('span', 'hud-elev');
  readout.append(where, latlon, elev);
  info.append(scale, readout);
  root.append(left, info);
  overlay.append(root);

  // ---- state ----
  const stored = load();
  let mapOn = stored === '1' ? true : stored === '0' ? false : innerWidth >= 900;
  map.hidden = !mapOn;
  let canvasH = app.canvas.clientHeight || innerHeight, aspect = camera.aspect;
  let pending = true, lastReadout = -Infinity;
  const shown = { dial: NaN, bearing: '', where: null, latlon: '', elev: '', scaleOn: null, metres: -1, px: -1, u: NaN, v: NaN, g: NaN, fov: NaN };
  const _f = new THREE.Vector3(), _d = new THREE.Vector3();

  // ---- compass ----
  function updateCompass() {
    const h = app.heading();
    const r = Math.round(h * 2) / 2;
    if (r !== shown.dial) { shown.dial = r; dial.style.transform = `rotate(${-r}deg)`; }
    const text = headingLabel(h, compassPoint(h));
    if (text !== shown.bearing) { shown.bearing = text; bearing.textContent = text; }
    return h;
  }
  function faceNorth() {
    if (app.state.mode === 'orbit') {
      const t = controls.target, off = _d.copy(camera.position).sub(t);
      const { dx, dz } = northOffset(Math.max(Math.hypot(off.x, off.z), 0.01), CONV);
      app.flyTo({ position: new THREE.Vector3(t.x + dx, t.y + off.y, t.z + dz), target: t.clone() }, { duration: 0.8, lift: 0 });
    } else {
      app.player.yaw = northYaw(CONV);
      app.player.refresh(); app.invalidate();
    }
  }
  compass.addEventListener('click', faceNorth);

  // ---- scale bar and position readout ----
  function setText(node, key, text) {
    if (shown[key] !== text) { shown[key] = text; node.textContent = text; }
  }
  function updateScale() {
    const on = app.state.mode === 'orbit';
    if (on !== shown.scaleOn) { shown.scaleOn = on; scale.hidden = !on; }
    if (!on) return;
    const mpp = metresPerPixel(camera.position.distanceTo(controls.target), camera.fov, canvasH);
    const { metres, px } = niceScale(mpp);
    const w = Math.round(px);
    if (w !== shown.px) { shown.px = w; bar.style.width = `${w}px`; }
    if (metres !== shown.metres) { shown.metres = metres; scaleText.textContent = formatScale(metres); }
  }
  function updateReadout() {
    const mode = app.state.mode;
    let y = null;
    if (mode === 'orbit') {
      _f.copy(controls.target);
      y = app.world.groundAt(_f.x, _f.z, null, { builtOnly: true }); // builtOnly: never stall a frame
    } else {
      _f.copy(mode === 'walk' && app.player.placed ? app.player.position : camera.position);
      y = _f.y;
    }
    const { lat, lon } = localToLatLon(_f.x, _f.z);
    setText(where, 'where', mode === 'fly' ? 'Camera' : '');
    setText(latlon, 'latlon', formatLatLon(lat, lon));
    setText(elev, 'elev', y === null ? '' : formatElevation(y));
  }

  // ---- minimap picture ----
  let ext = null, target = null, buffer = null, stale = true, timer = 0, lastMap = -Infinity, rush = false;
  let mapCost = 0; // milliseconds the last map picture took: it draws the whole campus and reads the pixels back
  const canFloat = renderer.extensions.has('EXT_color_buffer_float');
  const ctx = pic.getContext('2d');

  /** Draw the campus from straight above into the picture. Returns false if there is nothing to draw. */
  function renderMap() {
    const b = app.bounds;
    if (b.isEmpty() || !isFinite(b.min.x) || !isFinite(b.max.y)) return false;
    const e = mapExtent(b.min.x, b.min.z, b.max.x, b.max.z), half = e.size / 2;
    const cx = e.x0 + half, cz = e.z0 + half, top = b.max.y + 100;
    const began = performance.now();
    const cam = new THREE.OrthographicCamera(-half, half, half, -half, 1, top - b.min.y + 200);
    cam.up.set(0, 0, -1); // north (-Z) at the top of the picture, east to the right
    cam.position.set(cx, top, cz); cam.lookAt(cx, b.min.y, cz);
    cam.updateMatrixWorld(); cam.updateProjectionMatrix();
    if (!target) {
      // render targets skip tone mapping and sRGB output in three.js; read linear floats and do both here
      target = new THREE.WebGLRenderTarget(MAP_PX, MAP_PX, { type: canFloat ? THREE.FloatType : THREE.UnsignedByteType });
      buffer = canFloat ? new Float32Array(MAP_PX * MAP_PX * 4) : new Uint8Array(MAP_PX * MAP_PX * 4);
    }
    // keep the background clear so empty ground shows as paper, then put everything back as it was
    const prevTarget = renderer.getRenderTarget(), prevColor = renderer.getClearColor(new THREE.Color());
    const prevAlpha = renderer.getClearAlpha(), prevBg = app.scene.background;
    app.scene.background = null; renderer.setClearColor(0x000000, 0);
    try {
      app.renderPlain(cam, target);
      renderer.readRenderTargetPixels(target, 0, 0, MAP_PX, MAP_PX, buffer);
    } finally {
      app.scene.background = prevBg; renderer.setClearColor(prevColor, prevAlpha); renderer.setRenderTarget(prevTarget);
    }
    paint(buffer, canFloat ? 1 : 1 / 255);
    ext = e; lastMap = performance.now(); stale = false; mapCost = lastMap - began;
    shown.u = NaN; updateMarks(); // the extent may have changed
    return true;
  }
  function paint(src, k) {
    const img = ctx.createImageData(MAP_PX, MAP_PX), dst = img.data, rgb = [0, 0, 0];
    const exposure = renderer.toneMappingExposure;
    for (let y = 0; y < MAP_PX; y++) {
      const from = (MAP_PX - 1 - y) * MAP_PX * 4, to = y * MAP_PX * 4; // GL rows run bottom up
      for (let x = 0; x < MAP_PX * 4; x += 4) {
        const i = from + x, o = to + x;
        if (src[i + 3] * k < 0.5) { dst[o] = PAPER[0]; dst[o + 1] = PAPER[1]; dst[o + 2] = PAPER[2]; }
        else {
          toneMapToSrgb(src[i] * k, src[i + 1] * k, src[i + 2] * k, exposure, rgb);
          dst[o] = rgb[0]; dst[o + 1] = rgb[1]; dst[o + 2] = rgb[2];
        }
        dst[o + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
  }
  function schedule(delay) {
    if (!timer) timer = setTimeout(tryMap, delay);
  }
  function tryMap() {
    timer = 0;
    if (!mapOn || !stale) return;
    if (!app.isIdle()) return schedule(500); // never stall a moving camera
    // a slow GPU spends at most about 5% of the loading time on map pictures
    const wait = rush ? 0 : Math.max(MAP_GAP_MS, mapCost * 20) - (performance.now() - lastMap);
    if (wait > 0) return schedule(wait);
    rush = false;
    if (!renderMap()) schedule(1000);
  }
  function onTile() { stale = true; schedule(250); }
  function onComplete() { stale = true; rush = true; schedule(0); }

  // ---- minimap marks: where you are and which way you look ----
  function updateMarks(h = app.heading()) {
    if (!mapOn || !ext) return;
    app.focus(_f);
    const { u, v } = worldToMap(_f.x, _f.z, ext, MAP_PX);
    const g = Math.round((h - CONV) * 2) / 2; // grid bearing; the map is drawn grid north up
    const fov = Math.min(150, Math.round(horizontalFov(camera.fov, aspect)));
    if (Math.abs(u - shown.u) < 0.3 && Math.abs(v - shown.v) < 0.3 && g === shown.g && fov === shown.fov) return;
    shown.u = u; shown.v = v; shown.g = g; shown.fov = fov;
    dot.setAttribute('cx', u.toFixed(1)); dot.setAttribute('cy', v.toFixed(1));
    const r = 70, a0 = (g - fov / 2) * Math.PI / 180, a1 = (g + fov / 2) * Math.PI / 180;
    const p = (a) => `${(u + Math.sin(a) * r).toFixed(1)} ${(v - Math.cos(a) * r).toFixed(1)}`;
    wedge.setAttribute('d', `M${u.toFixed(1)} ${v.toFixed(1)} L${p(a0)} A${r} ${r} 0 0 1 ${p(a1)} Z`);
  }

  // ---- moving the view from the map ----
  function moveTo(x, z, duration) {
    const mode = app.state.mode;
    if (mode === 'orbit') {
      const t = controls.target, off = _d.copy(camera.position).sub(t);
      const y = app.world.groundAt(x, z, null, { builtOnly: true }) ?? t.y;
      const next = new THREE.Vector3(x, y, z);
      app.world.prioritize?.(x, z);
      app.flyTo({ position: next.clone().add(off), target: next }, { duration });
    } else if (mode === 'walk') {
      app.player.teleport(x, z);
    } else {
      camera.position.x = x; camera.position.z = z; app.invalidate();
    }
  }
  function onMapClick(e) {
    if (!ext) return;
    const r = view.getBoundingClientRect(); // a click, not a frame: one layout read is fine
    const { x, z } = mapToWorld(((e.clientX - r.left) / r.width) * MAP_PX, ((e.clientY - r.top) / r.height) * MAP_PX, ext, MAP_PX);
    moveTo(x, z, 0.9);
  }
  const KEYS = { ArrowUp: [0, -1], ArrowDown: [0, 1], ArrowLeft: [-1, 0], ArrowRight: [1, 0] };
  function onMapKey(e) {
    const k = KEYS[e.key];
    if (!k || e.ctrlKey || e.altKey || e.metaKey) return;
    e.preventDefault(); e.stopPropagation(); // keep the walk and fly keys from moving the player too
    app.focus(_f);
    moveTo(_f.x + k[0] * KEY_STEP, _f.z + k[1] * KEY_STEP, 0);
  }
  view.addEventListener('click', onMapClick);
  view.addEventListener('keydown', onMapKey);

  // ---- map on and off ----
  function setMap(on) {
    on = !!on;
    if (on === mapOn) return;
    mapOn = on; map.hidden = !on; save(on);
    if (on) { shown.u = NaN; updateMarks(); if (stale) schedule(0); }
    app.emit('hud:map', { on });
  }
  close.addEventListener('click', () => {
    const had = document.activeElement === close;
    setMap(false);
    if (had) compass.focus(); // focus was on the button that just disappeared
  });

  // ---- events ----
  const offs = [
    app.on('camera', () => { pending = true; updateMarks(updateCompass()); }),
    app.on('frame', ({ time }) => {
      if (!pending || time - lastReadout < READOUT_MS) return;
      pending = false; lastReadout = time;
      updateScale(); updateReadout();
    }),
    app.on('mode', () => { pending = true; lastReadout = -Infinity; }),
    app.on('resize', ({ height }) => { canvasH = app.canvas.clientHeight || height; aspect = camera.aspect; pending = true; shown.fov = NaN; }),
    app.on('tile', onTile),
    app.on('scene:complete', onComplete),
    app.on('scene:start', () => { stale = true; }),
  ];
  updateMarks(updateCompass());
  if (app.state.ready) schedule(0);

  return {
    setMap,
    get map() { return mapOn; },
    setVisible(on) { root.hidden = !on; },
    dispose() {
      for (const off of offs) off();
      clearTimeout(timer); timer = 0;
      target?.dispose(); target = null;
      root.remove();
    },
  };
}
