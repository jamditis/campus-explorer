// Place-name labels drawn over the 3D view. Each label is a button in #overlay anchored 6 m above
// the top of the model at its place; clicking it flies there. Layout runs only when the camera moved,
// writes transforms only, and never reads layout in the frame path (sizes are measured once per label).
import * as THREE from 'three';
import { labelPriority, distanceOpacity, inRange, declutter, sourceTitle } from './labels-math.js';

const STORE = 'campus-labels';
const ABOVE = 6;            // metres above the top of the model
const FAR = 1400;           // hide beyond this
const FADE_FROM = 800;      // start fading here
const PARKING = 350;        // lots only show within this
const NEAR_MOVING = 12;     // in walk and fly, hide labels nearer than this
const TRIES_PER_FRAME = 3;  // ground lookups per frame while anchors are missing
const RETRY_MS = 1500;      // wait before asking again for a place that missed
const CONFIRM_MS = 4000;    // wait between confirming lookups for a place that hit
const CONFIRMS = 3;         // hits needed before a place stops being asked
const HIGHLIGHT_MS = 6000;

/**
 * Create the place labels.
 * @param app the shared app object (see docs/VIEWER.md)
 * @returns {{ setVisible(on: boolean): void, readonly visible: boolean, highlight(place: object|null): void, dispose(): void }}
 */
export function createLabels(app) {
  const { camera } = app;
  const host = document.getElementById('overlay') || document.body;
  const layer = document.createElement('div');
  layer.className = 'lbl-layer';
  host.appendChild(layer);

  let labels = [];          // { place, el, w, h, anchor: Vector3, hit, checks, found, nextTry, shown, key, opacity }
  let visible = readStored();
  let highlighted = null;   // place object
  let highlightTimer = 0;
  let dirty = true;         // relayout on the next frame even if the camera did not move
  let width = innerWidth, height = innerHeight;
  const v = new THREE.Vector3();
  layer.hidden = !visible;

  function readStored() {
    try { return localStorage.getItem(STORE) !== 'off'; } catch { return true; }
  }

  function floorY() {
    return Number.isFinite(app.bounds.min.y) ? app.bounds.min.y + 25 : 150;
  }

  function build() {
    for (const l of labels) l.el.remove();
    labels = (app.places || []).filter(p => p && Number.isFinite(p.x) && Number.isFinite(p.z) && p.name).map(place => {
      const el = document.createElement('button');
      el.type = 'button';
      el.className = `lbl lbl-${place.kind || 'place'}`;
      el.title = sourceTitle(place);
      const text = document.createElement('span');
      text.className = 'lbl-text';
      text.textContent = place.name;
      const stem = document.createElement('span');
      stem.className = 'lbl-stem';
      stem.setAttribute('aria-hidden', 'true');
      el.append(text, stem);
      el.addEventListener('click', () => app.goToPlace(place));
      layer.appendChild(el);
      return { place, el, w: 0, h: 0, anchor: new THREE.Vector3(place.x, floorY() + ABOVE, place.z), hit: false, checks: CONFIRMS, found: false, nextTry: 0, shown: false, key: '', opacity: -1 };
    });
    measure();
    dirty = true;
  }

  // One layout read for all labels, here and never per frame (they start hidden but laid out).
  // While the layer is switched off nothing has a size, so this runs again when it is switched on.
  function measure(all = false) {
    if (!visible) return;
    for (const l of labels) if (all || !l.w) { l.w = l.el.offsetWidth; l.h = l.el.offsetHeight; }
  }

  // Top of the model at a place. builtOnly never stalls a frame; it returns null until the tile's
  // collision is ready, so places that miss are asked again later. Collision for a tile is built mesh
  // by mesh, so the first hit can be the terrain under a roof whose mesh is not ready yet: a hit is
  // confirmed a few times, seconds apart, keeping the highest, before the place stops being asked.
  function pump(now) {
    let budget = TRIES_PER_FRAME;
    for (const l of labels) {
      if (budget <= 0) break;
      if (l.found || now < l.nextTry) continue;
      budget--;
      const y = app.world.groundAt(l.place.x, l.place.z, null, { builtOnly: true });
      if (y != null && Number.isFinite(y)) {
        if (!l.hit || y + ABOVE > l.anchor.y + 0.01) { l.anchor.y = y + ABOVE; dirty = true; }
        l.hit = true;
        if (--l.checks <= 0) l.found = true; else l.nextTry = now + CONFIRM_MS;
      } else {
        l.nextTry = now + RETRY_MS;
        const fallback = floorY() + ABOVE;
        if (!l.hit && l.anchor.y !== fallback) { l.anchor.y = fallback; dirty = true; }
      }
    }
  }

  function hide(l) {
    if (!l.shown) return;
    l.shown = false; l.el.classList.remove('lbl-shown');
  }

  function layout() {
    dirty = false;
    if (!visible || !labels.length) return;
    const moving = app.state.mode !== 'orbit';
    const max = width < 700 ? 12 : 28;
    const items = [], owners = [];
    for (const l of labels) {
      const isOn = l.place === highlighted;
      const dist = camera.position.distanceTo(l.anchor);
      const ok = isOn ? !(moving && dist < NEAR_MOVING) : inRange(l.place.kind, dist, { far: FAR, parking: PARKING, minimum: moving ? NEAR_MOVING : 0 });
      if (!ok) { hide(l); continue; }
      // camera space first: anything at or behind the camera plane has no sensible projection
      v.copy(l.anchor).applyMatrix4(camera.matrixWorldInverse);
      if (v.z > -camera.near) { hide(l); continue; }
      v.applyMatrix4(camera.projectionMatrix);
      const sx = (v.x + 1) / 2 * width, sy = (1 - v.y) / 2 * height;
      // anchor is the bottom centre of the label (the dot at the foot of the stem)
      const x = sx - l.w / 2, y = sy - l.h;
      // only whole labels: one cut by the screen edge reads as a different name
      if (x < 0 || x + l.w > width || y < 0 || sy > height) { hide(l); continue; }
      items.push({ x, y, w: l.w, h: l.h, priority: labelPriority(l.place.kind, l.place.r, dist), forced: isOn, dist });
      owners.push(l);
    }
    const keep = new Set(declutter(items, { max, pad: 3 }));
    for (let i = 0; i < items.length; i++) {
      const l = owners[i], it = items[i];
      if (!keep.has(i)) { hide(l); continue; }
      // the percentages put the label's bottom centre on the anchor whatever its real size, so a
      // stale measurement can only affect decluttering, never where the dot lands
      const key = `translate3d(${(it.x + it.w / 2).toFixed(1)}px,${(it.y + it.h).toFixed(1)}px,0) translate(-50%,-100%)`;
      if (key !== l.key) { l.key = key; l.el.style.transform = key; }
      const op = it.forced ? 1 : Math.round(distanceOpacity(it.dist, FADE_FROM, FAR) * 20) / 20;
      if (op !== l.opacity) { l.opacity = op; l.el.style.opacity = String(op); }
      if (!l.shown) { l.shown = true; l.el.classList.add('lbl-shown'); }
    }
  }

  function setVisible(on) {
    on = !!on;
    if (on === visible) return;
    visible = on; layer.hidden = !on;
    measure();
    if (!on) for (const l of labels) hide(l);
    try { localStorage.setItem(STORE, on ? 'on' : 'off'); } catch { /* private mode */ }
    dirty = true;
    app.emit('labels', { on });
  }

  function highlight(place) {
    clearTimeout(highlightTimer);
    // match by identity, falling back to the OSM id so a copy of a place still finds its label
    const l = place && labels.find(x => x.place === place || (place.osm && x.place.osm === place.osm && x.place.name === place.name));
    highlighted = l ? l.place : place || null;
    for (const x of labels) x.el.classList.toggle('lbl-on', x.place === highlighted);
    dirty = true;
  }

  const offs = [
    app.on('places', build),
    app.on('tile', () => { for (const l of labels) if (!l.found) l.nextTry = 0; }),
    // the camera event comes after the controls update and before drawing, so labels match this frame
    app.on('camera', () => layout()),
    // the label font size changes at the phone breakpoint, so sizes are read again on resize
    app.on('resize', ({ width: w, height: h }) => { width = w; height = h; measure(true); dirty = true; }),
    app.on('mode', () => { dirty = true; }),
    app.on('place', ({ place }) => {
      highlight(place);
      highlightTimer = setTimeout(() => { if (highlighted === place || highlighted?.osm === place?.osm) highlight(null); }, HIGHLIGHT_MS);
    }),
    app.on('frame', ({ time }) => {
      if (visible && labels.length) pump(time ?? performance.now());
      if (dirty) layout();
    }),
  ];
  if (app.places?.length) build();
  document.fonts?.ready.then(() => { measure(true); dirty = true; });

  return {
    setVisible,
    get visible() { return visible; },
    highlight,
    dispose() {
      clearTimeout(highlightTimer);
      for (const off of offs) off();
      layer.remove(); labels = [];
    },
  };
}
