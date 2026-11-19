// Guided tour: the camera visits a fixed list of places, circles each one slowly while a caption
// card names it, then returns to the overview. Built on app.flyTo; any direct input on the view stops it.
import * as THREE from 'three';
import { selectStops, tourCaption, southWestOffset, TOUR_NAMES } from './labels-math.js';

const FLY_SECONDS = 3.2;
const CIRCLE_SECONDS = 7;
const HOLD_SECONDS = 5;        // reduced motion: hold still instead of circling
const DEG_PER_SECOND = 4;
// keys that move the camera in fly or walk; pressing one means the user wants the view back
const MOVE_CODES = new Set(['KeyW', 'KeyA', 'KeyS', 'KeyD', 'KeyQ', 'KeyE', 'KeyC', 'Space',
  'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'PageUp', 'PageDown']);

/**
 * Create the guided tour.
 * @param app the shared app object (see docs/VIEWER.md)
 * @returns {{ start(): void, stop(): void, next(): void, previous(): void, readonly running: boolean, dispose(): void }}
 */
export function createTour(app) {
  const { camera, controls, canvas } = app;
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let running = false, index = 0, stops = [], token = 0;
  let circling = null;          // { until, resolve, spin } while holding at a stop
  const offset = new THREE.Vector3();

  const card = buildCard();

  function buildCard() {
    const root = document.createElement('section');
    root.className = 'tour-card';
    root.setAttribute('aria-label', 'Guided tour');
    root.hidden = true;
    root.innerHTML = `
      <div class="tour-head"><h2 class="tour-name" aria-live="polite"></h2><span class="tour-count"></span></div>
      <p class="tour-details"></p>
      <div class="tour-buttons">
        <button type="button" class="tour-prev">Previous</button>
        <button type="button" class="tour-next">Next</button>
        <button type="button" class="tour-stop">Stop tour</button>
      </div>
      <p class="tour-source">Names from OpenStreetMap</p>`;
    root.querySelector('.tour-prev').addEventListener('click', previous);
    root.querySelector('.tour-next').addEventListener('click', next);
    root.querySelector('.tour-stop').addEventListener('click', () => stop());
    (document.getElementById('overlay') || document.body).appendChild(root);
    return root;
  }

  function render() {
    card.hidden = !running;
    if (!running) return;
    const place = stops[index];
    const c = tourCaption(place, index, stops.length);
    card.querySelector('.tour-name').textContent = c.title;
    card.querySelector('.tour-count').textContent = c.counter;
    const details = card.querySelector('.tour-details');
    details.textContent = c.details.join(' · ');
    details.hidden = !c.details.length;
    card.querySelector('.tour-source').textContent = c.source;
    card.querySelector('.tour-prev').disabled = index === 0;
    card.querySelector('.tour-next').textContent = index === stops.length - 1 ? 'Finish' : 'Next';
  }

  function announce() {
    render();
    app.emit('tour', { running, index, count: stops.length, place: running ? stops[index] : null });
  }

  function poseFor(place) {
    const floor = Number.isFinite(app.bounds.min.y) ? app.bounds.min.y + 20 : 130;
    const y = app.world.groundAt(place.x, place.z, null, { builtOnly: true }) ?? floor;
    const target = new THREE.Vector3(place.x, y, place.z);
    const o = southWestOffset(place.r);
    return { target, position: target.clone().add(new THREE.Vector3(o.dx, o.dy, o.dz)) };
  }

  // Wait at a stop, circling (or holding still) until time runs out or the tour moves on.
  function hold() {
    return new Promise(resolve => {
      const seconds = calm ? HOLD_SECONDS : CIRCLE_SECONDS;
      circling = { until: performance.now() + seconds * 1000, resolve, spin: !calm };
    });
  }

  function endHold() {
    if (!circling) return;
    const c = circling; circling = null; c.resolve();
  }

  async function run() {
    const my = ++token;
    while (running && my === token && index < stops.length) {
      const place = stops[index];
      announce();
      app.emit('place', { place });
      app.world.prioritize(place.x, place.z);
      const arrived = await app.flyTo(poseFor(place), { duration: FLY_SECONDS });
      if (my !== token) return;
      if (!arrived) { stop({ halt: false }); return; }
      await hold();
      if (my !== token) return;
      index++;
    }
    if (my !== token || !running) return;
    // the last stop is done: hand the view back at the overview
    running = false; token++; announce();
    app.overview();
  }

  /** Start the tour from the first stop. */
  function start() {
    stops = selectStops(app.places, TOUR_NAMES);
    if (!stops.length) { app.toast('No tour stops are loaded yet'); return; }
    running = true; index = 0;
    run();
  }

  /** Stop the tour and leave the camera where it is. */
  function stop({ halt = true } = {}) {
    if (!running) return;
    running = false; token++;
    endHold();
    // a flight in progress would otherwise carry on to the stop; a zero-length move to here ends it
    if (halt && app.state.mode === 'orbit') app.flyTo({ position: camera.position.clone(), target: controls.target.clone() }, { duration: 0 });
    announce();
  }

  function jump(to) {
    if (!running) return;
    endHold();
    if (to >= stops.length) { index = stops.length; token++; running = false; announce(); app.overview(); return; }
    index = Math.max(0, to);
    run();
  }
  /** Go on to the next stop (or finish after the last). */
  function next() { jump(index + 1); }
  /** Go back one stop. */
  function previous() { jump(index - 1); }

  // ---- circling ----
  const _y = new THREE.Vector3(0, 1, 0);
  function onFrame({ dt }) {
    if (!circling) return;
    if (performance.now() >= circling.until) { endHold(); return; }
    if (!circling.spin || app.state.mode !== 'orbit') return;
    // rotate the camera about the vertical through the orbit target; the loop redraws because it moved
    offset.copy(camera.position).sub(controls.target).applyAxisAngle(_y, THREE.MathUtils.degToRad(DEG_PER_SECOND) * dt);
    camera.position.copy(controls.target).add(offset);
    camera.lookAt(controls.target);
  }

  // ---- anything the user does to the view stops the tour ----
  const userInput = () => stop({ halt: false });
  function onKey(e) {
    if (!running) return;
    if (e.key === 'Escape') { stop(); return; }
    if (!MOVE_CODES.has(e.code) || e.ctrlKey || e.metaKey || e.altKey) return;
    const t = e.target, tag = t?.tagName;
    // typing in a field, or Space on a button (including the tour's own), is not a camera move
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || t?.isContentEditable) return;
    if (tag === 'BUTTON' && (e.code === 'Space' || e.code.startsWith('Arrow'))) return;
    stop(); // halts the flight too: unlike a pointer or wheel event, a key does not cancel a camera move by itself
  }
  const onMode = ({ mode }) => { if (mode !== 'orbit') stop({ halt: false }); };

  for (const type of ['pointerdown', 'wheel', 'touchstart']) canvas.addEventListener(type, userInput, { passive: true });
  addEventListener('keydown', onKey);
  const offs = [app.on('frame', onFrame), app.on('mode', onMode)];

  return {
    start, stop: () => stop(), next, previous,
    get running() { return running; },
    get index() { return index; },
    dispose() {
      stop();
      for (const type of ['pointerdown', 'wheel', 'touchstart']) canvas.removeEventListener(type, userInput);
      removeEventListener('keydown', onKey);
      for (const off of offs) off();
      card.remove();
    },
  };
}
