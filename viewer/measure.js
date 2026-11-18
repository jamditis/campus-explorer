// Distance and height measuring tool for orbit mode. Click points on the model to build a path;
// the path is drawn over the model and its lengths are shown as labels in #overlay.
// It only watches pointer events and never calls preventDefault, so dragging still orbits.
import * as THREE from 'three';
import { formatDistance } from './geo.js';
import { isClick, pathTotals, formatRise, formatSlope, formatBearing } from './measure-math.js';

const CORE_PX = 3, OUTLINE_PX = 6, DOT_PX = 4, DOT_OUTLINE_PX = 6;
const ACCENT = '#b3282d';
const HINT = 'Click two or more points on the model';
const NOTE = 'Measured on the model, a work in progress. Not a survey.';
const nextFrame = () => new Promise(r => requestAnimationFrame(() => setTimeout(r, 0)));

/**
 * Create the measuring tool. Returns { setActive(on), active, clear(), dispose() }.
 * Emits `measure` { active, count } whenever the tool turns on or off or the path changes.
 */
export function createMeasure(app) {
  const { camera, canvas, scene } = app;
  const overlay = document.getElementById('overlay') || document.body;
  const points = [];
  let active = false, busy = false, press = null, savedCursor = '';
  const pressed = new Set();

  // ---- 3D: thin camera-facing quads for the line, small spheres for the points ----
  const group = new THREE.Group(); group.name = 'measure';
  const mat = (color, order) => {
    const m = new THREE.MeshBasicMaterial({ color, depthTest: false, depthWrite: false, transparent: true, fog: false, toneMapped: false, side: THREE.DoubleSide });
    return { m, order };
  };
  const outlineMat = mat('#ffffff', 1000), coreMat = mat(ACCENT, 1001), dotOutlineMat = mat('#ffffff', 1002), dotMat = mat(ACCENT, 1003);
  const outline = strip(outlineMat), core = strip(coreMat);
  const dotGeo = new THREE.SphereGeometry(1, 16, 10);
  const dots = new THREE.Group(); dots.name = 'measure_points';
  group.add(outline, core, dots);

  function strip({ m, order }) {
    const mesh = new THREE.Mesh(new THREE.BufferGeometry(), m);
    mesh.renderOrder = order; mesh.frustumCulled = false; // vertices move every frame
    mesh.castShadow = mesh.receiveShadow = false;
    return mesh;
  }
  function dot() {
    const g = new THREE.Group();
    for (const { m, order } of [dotOutlineMat, dotMat]) {
      const s = new THREE.Mesh(dotGeo, m); s.renderOrder = order; s.frustumCulled = false;
      s.castShadow = s.receiveShadow = false; g.add(s);
    }
    return g;
  }

  /** World units per screen pixel at distance d from the camera. */
  function perPixel(d) {
    const h = canvas.clientHeight || innerHeight;
    return 2 * Math.max(d, camera.near) * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) / h;
  }

  const _d = new THREE.Vector3(), _v = new THREE.Vector3(), _s = new THREE.Vector3(), _up = new THREE.Vector3();
  /** Rebuild one strip so each segment is `px` pixels wide on screen at both ends. */
  function fillStrip(mesh, px) {
    const n = points.length - 1, geo = mesh.geometry;
    if (n < 1) { geo.setDrawRange(0, 0); return; }
    let pos = geo.getAttribute('position');
    if (!pos || pos.count < n * 4) {
      pos = new THREE.BufferAttribute(new Float32Array(n * 12), 3); pos.setUsage(THREE.DynamicDrawUsage);
      geo.setAttribute('position', pos);
      const idx = [];
      for (let i = 0; i < n; i++) { const k = i * 4; idx.push(k, k + 1, k + 2, k + 2, k + 1, k + 3); }
      geo.setIndex(idx);
    }
    camera.getWorldDirection(_up);
    for (let i = 0; i < n; i++) {
      const a = points[i], b = points[i + 1];
      _d.subVectors(b, a);
      [a, b].forEach((p, j) => {
        _v.subVectors(p, camera.position);
        _s.crossVectors(_d, _v);
        if (_s.lengthSq() < 1e-10) _s.crossVectors(_d, _up); // segment points straight at the camera
        _s.normalize().multiplyScalar(perPixel(_v.length()) * px / 2);
        const k = i * 4 + j * 2;
        pos.setXYZ(k, p.x + _s.x, p.y + _s.y, p.z + _s.z);
        pos.setXYZ(k + 1, p.x - _s.x, p.y - _s.y, p.z - _s.z);
      });
    }
    pos.needsUpdate = true;
    geo.setDrawRange(0, n * 6);
  }

  function updateScene() {
    fillStrip(outline, OUTLINE_PX); fillStrip(core, CORE_PX);
    dots.children.forEach((g, i) => {
      const k = perPixel(camera.position.distanceTo(points[i]));
      g.position.copy(points[i]);
      g.children[0].scale.setScalar(k * DOT_OUTLINE_PX);
      g.children[1].scale.setScalar(k * DOT_PX);
    });
  }

  // ---- DOM: toolbar, segment labels and the totals card ----
  const bar = el('div', 'msr-bar');
  bar.setAttribute('role', 'toolbar'); bar.setAttribute('aria-label', 'Measure'); bar.hidden = true;
  const hint = el('p', 'msr-hint', HINT);
  const buttons = el('div', 'msr-buttons');
  const undoBtn = button('Undo point', 'Undo the last point (Backspace or Z)', undo);
  const clearBtn = button('Clear', 'Clear the path', () => clear());
  const doneBtn = button('Done', 'Stop measuring (Escape)', () => setActive(false));
  doneBtn.classList.add('msr-done');
  buttons.append(undoBtn, clearBtn, doneBtn); bar.append(hint, buttons);
  const layer = el('div', 'msr-layer');
  const card = el('div', 'msr-card'); card.setAttribute('role', 'status'); card.setAttribute('aria-live', 'polite');
  layer.append(card);
  overlay.append(layer, bar);

  function el(tag, cls, text) {
    const e = document.createElement(tag); e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function button(text, title, fn) {
    const b = el('button', 'msr-btn', text); b.type = 'button'; b.title = title;
    b.addEventListener('click', fn);
    return b;
  }

  /** Recreate segment labels and card text after the path changed. */
  function renderLabels() {
    layer.querySelectorAll('.msr-seg').forEach(n => n.remove());
    const t = pathTotals(points);
    t.segments.forEach(len => layer.insertBefore(el('div', 'msr-seg', formatDistance(len)), card));
    card.replaceChildren();
    if (t.count >= 2) {
      const dl = el('dl', 'msr-totals');
      const row = (k, v) => { if (v) dl.append(el('dt', '', k), el('dd', '', v)); };
      if (t.count > 2) row('Path', formatDistance(t.path));
      row('Straight line', formatDistance(t.straight));
      row('Horizontal', formatDistance(t.horizontal));
      row('Height', formatRise(t.rise));
      row('Slope', formatSlope(t.slope));
      row('Bearing', t.bearing === null ? '' : `${formatBearing(t.bearing)} (true)`);
      card.append(dl, el('p', 'msr-note', NOTE));
    }
    card.hidden = t.count < 2;
    undoBtn.disabled = clearBtn.disabled = !points.length;
    place();
  }

  const _p = new THREE.Vector3();
  /** Screen position of a world point, or null when it is behind the camera. */
  function project(v) {
    _p.copy(v).project(camera);
    if (_p.z > 1 || _p.z < -1) return null;
    const r = canvas.getBoundingClientRect();
    return { x: r.left + (_p.x + 1) / 2 * r.width, y: r.top + (1 - _p.y) / 2 * r.height };
  }
  /** Move the labels to follow the camera. */
  function place() {
    const segs = layer.querySelectorAll('.msr-seg');
    segs.forEach((n, i) => {
      const s = project(_v.addVectors(points[i], points[i + 1]).multiplyScalar(0.5));
      n.hidden = !s;
      if (s) n.style.transform = `translate(${s.x}px, ${s.y}px) translate(-50%, -50%)`;
    });
    if (card.hidden || !points.length) return;
    const s = project(points[points.length - 1]);
    card.style.visibility = s ? '' : 'hidden';
    if (!s) return;
    // above and to the right of the last point, kept on screen
    const w = card.offsetWidth, h = card.offsetHeight;
    const x = THREE.MathUtils.clamp(s.x + 14, 8, Math.max(8, innerWidth - w - 8));
    const y = THREE.MathUtils.clamp(s.y - h - 14, 8, Math.max(8, innerHeight - h - 8));
    card.style.transform = `translate(${x}px, ${y}px)`;
  }

  // ---- path editing ----
  function changed(emit = true) {
    while (dots.children.length < points.length) dots.add(dot());
    while (dots.children.length > points.length) dots.remove(dots.children[dots.children.length - 1]);
    updateScene(); renderLabels(); app.invalidate();
    if (emit) app.emit('measure', { active, count: points.length });
  }
  function add(p) { points.push(p.clone()); changed(); }
  function undo() { if (points.length) { points.pop(); changed(); } }
  /** Remove every point of the path. */
  function clear() { if (points.length) { points.length = 0; changed(); } }

  // ---- input: watch clicks, never block orbiting ----
  function onDown(e) {
    pressed.add(e.pointerId);
    // a second finger means a pinch or two-finger pan, not a click
    press = pressed.size === 1 && e.isPrimary && (e.button === 0 || e.pointerType === 'touch')
      ? { id: e.pointerId, x: e.clientX, y: e.clientY, t: performance.now() } : null;
  }
  function onUp(e) {
    pressed.delete(e.pointerId);
    const p = press; press = null;
    if (!active || !p || p.id !== e.pointerId) return;
    if (isClick(p, { x: e.clientX, y: e.clientY, t: performance.now() })) pickAt(e.clientX, e.clientY);
  }
  function onCancel(e) { pressed.delete(e.pointerId); press = null; }

  async function pickAt(x, y) {
    if (busy) return;
    busy = true; canvas.style.cursor = 'progress';
    let hit = null;
    try {
      await nextFrame(); // let the cursor show: the first pick in an area builds collision data
      if (active) hit = app.world.pick(x, y);
    } finally {
      busy = false; canvas.style.cursor = active ? 'crosshair' : savedCursor;
    }
    if (!active) return;
    if (hit) add(hit.point); else app.toast('No model surface there');
  }

  function onKey(e) {
    if (!active || e.altKey) return;
    const t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (e.key === 'Escape') {
      if (points.length) clear(); else setActive(false);
    } else if (e.key === 'Backspace' || e.key === 'z' || e.key === 'Z') {
      undo();
    } else return;
    e.preventDefault();
  }

  function onCamera() { if (active && points.length) { updateScene(); place(); } }
  function onMode({ mode }) { if (mode !== 'orbit' && active) setActive(false); }
  function onResize() { if (active) { reserve(); onCamera(); } }

  // other top-centre cards (the hunt) sit below the toolbar
  function reserve() {
    document.documentElement.style.setProperty('--msr-bar-h', active ? `${bar.offsetHeight + 8}px` : '0px');
  }

  canvas.addEventListener('pointerdown', onDown, { passive: true });
  canvas.addEventListener('pointerup', onUp, { passive: true });
  canvas.addEventListener('pointercancel', onCancel, { passive: true });
  addEventListener('keydown', onKey);
  const offs = [app.on('camera', onCamera), app.on('mode', onMode), app.on('resize', onResize)];

  /** Turn the tool on or off. Turning it on switches to orbit mode; turning it off clears the path. */
  function setActive(on) {
    on = !!on;
    if (on === active) return;
    if (on && app.state.mode !== 'orbit') app.setMode('orbit');
    active = on;
    if (on) {
      savedCursor = canvas.style.cursor; canvas.style.cursor = 'crosshair';
      scene.add(group); bar.hidden = false; layer.hidden = false;
      renderLabels();
    } else {
      canvas.style.cursor = savedCursor;
      points.length = 0; changed(false);
      scene.remove(group); bar.hidden = true; layer.hidden = true;
    }
    reserve(); app.invalidate();
    app.emit('measure', { active, count: points.length });
  }

  layer.hidden = true;
  return {
    setActive,
    get active() { return active; },
    get points() { return points.map(p => p.clone()); },
    clear,
    dispose() {
      setActive(false);
      canvas.removeEventListener('pointerdown', onDown);
      canvas.removeEventListener('pointerup', onUp);
      canvas.removeEventListener('pointercancel', onCancel);
      removeEventListener('keydown', onKey);
      offs.forEach(off => off());
      bar.remove(); layer.remove();
      for (const { m } of [outlineMat, coreMat, dotOutlineMat, dotMat]) m.dispose();
      outline.geometry.dispose(); core.geometry.dispose(); dotGeo.dispose();
      document.documentElement.style.removeProperty('--msr-bar-h');
    },
  };
}
