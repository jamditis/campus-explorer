// Film mode: plays the shots of cinema-math.js full screen between letterbox bars, with a fade at each cut,
// golden-hour and night light from the real sunset of the date shown, and a caption naming the place. The
// bars, fades and captions are page elements, so the mode costs nothing to draw. Any input on the view, a
// camera move another module asks for, or Esc stops it and gives the view, the light and the panel back.
import { CAMPUS } from './geo.js';
import { sunTimes } from './sun.js';
import { SHOTS, poseAt, lightOffset, letterbox } from './cinema-math.js';

const FADE_MS = 700;          // each half of a cut (to black, from black)
const LOAD_WAIT_MS = 5000;    // longest wait at a cut for the tiles under the next shot

/**
 * @param app the shared app object (see docs/VIEWER.md)
 * @returns {{ start(): void, stop(): void, readonly running: boolean }}
 */
export function createCinema(app) {
  const { camera, controls, canvas } = app;
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let running = false, token = 0, shot = null, t0 = 0, groundY = 0, before = null;

  const root = document.createElement('div');
  root.className = 'cine'; root.hidden = true;
  root.innerHTML = `<div class="cine-bar cine-top"></div><div class="cine-bar cine-bottom"><p class="cine-caption" aria-live="polite"></p>
    <button type="button" class="cine-stop">Stop film</button></div><div class="cine-fade"></div>`;
  (document.getElementById('overlay') || document.body).appendChild(root);
  const fade = root.querySelector('.cine-fade'), caption = root.querySelector('.cine-caption');
  root.querySelector('.cine-stop').addEventListener('click', () => stop());

  function size() {
    const h = letterbox(innerWidth, innerHeight);
    for (const bar of root.querySelectorAll('.cine-bar')) bar.style.height = `${Math.max(h, 44)}px`;
  }
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const black = on => { fade.classList.toggle('on', on); return sleep(calm ? FADE_MS * 1.5 : FADE_MS); };

  function lightFor(s) {
    const off = lightOffset(s); if (off === null) return null;
    const { sunset } = sunTimes(app.time.date, CAMPUS.lat, CAMPUS.lon);
    return sunset ? new Date(sunset.getTime() + off * 60000) : null;
  }
  function apply(p) {
    camera.position.set(...p.position); controls.target.set(...p.target); camera.lookAt(controls.target);
  }

  async function run() {
    const my = ++token;
    for (const s of SHOTS) {
      await black(true); if (my !== token) return;
      // the tiles under the camera and its target first (the lite profile keeps only those near the target)
      const p0 = poseAt(s, 0, 0), spots = [[p0.position[0], p0.position[2]], [p0.target[0], p0.target[2]]];
      if (s.ground) spots.push(s.ground);
      const until = performance.now() + LOAD_WAIT_MS;
      // asked again on every check: a tile leaves the urgent list when it starts loading, and the lite profile's
      // rebalance (around the old shot's target) could drop it before the check sees it
      for (;;) {
        for (const [x, z] of spots) app.world.prioritize(x, z);
        if (spots.every(([x, z]) => app.world.isLoaded(x, z)) || performance.now() >= until) break;
        await sleep(200); if (my !== token) return;
      }
      if (s.ground) groundY = app.world.groundAt(s.ground[0], s.ground[1]) ?? (isFinite(app.bounds.min.y) ? app.bounds.min.y : 120);
      const when = lightFor(s); if (when) app.setTime(when);
      caption.textContent = s.caption;
      shot = s; t0 = performance.now(); apply(poseAt(s, 0, groundY, calm)); app.invalidate();
      await black(false); if (my !== token) return;
      await sleep(s.seconds * 1000 - FADE_MS); if (my !== token) return;
    }
    stop();
  }

  function onFrame() {
    if (!shot) return;
    apply(poseAt(shot, (performance.now() - t0) / 1000, groundY, calm)); // the loop redraws because the camera moved
  }

  async function start() {
    if (running) return;
    // a walk still finding its ground has no place to come back to yet (player.position is stale until it lands)
    while (app.state.mode === 'walk' && app.player.busy) await sleep(200);
    if (running) return;
    if (!app.state.ready) { app.toast('The campus is still loading'); return; }
    app.cancelFly('cinema');
    before = {
      position: camera.position.clone(), quaternion: camera.quaternion.clone(), target: controls.target.clone(),
      date: app.time.date, preset: app.time.preset, mode: app.state.mode,
      walker: app.state.mode === 'walk' ? app.player.position.clone() : null, // the feet, not the eye or a third-person camera
    };
    const go = () => {
      running = true; root.hidden = false; size();
      document.body.classList.add('cinema'); controls.enabled = false;
      app.emit('cinema', { running: true });
      run();
    };
    if (app.state.mode !== 'orbit') app.setMode('orbit').then(go); else go();
  }

  /** Stop the film. `keepView`: the user has taken the view (a mode key): give back the light and panel only. */
  function stop({ keepView = false } = {}) {
    if (!running) return;
    running = false; token++; shot = null;
    fade.classList.remove('on'); root.hidden = true;
    document.body.classList.remove('cinema'); controls.enabled = app.state.mode === 'orbit';
    if (before) {
      const b = before; before = null;
      if (b.preset) app.resetTime(); else app.setTime(b.date);
      if (keepView) { app.invalidate(); app.emit('cinema', { running: false }); return; }
      camera.position.copy(b.position); controls.target.copy(b.target);
      if (b.mode === 'orbit') controls.update();
      else {
        // fly and walk: the camera as it was, not passed through orbit's limits (it may have looked up at the
        // target); setMode switches before the next frame, so orbit never applies them
        camera.quaternion.copy(b.quaternion);
        if (b.mode === 'fly') app.setMode('fly');
        else app.setMode('walk', { at: b.walker }); // where the walker stood (third person: not the camera)
      }
    }
    app.invalidate(); app.emit('cinema', { running: false });
  }

  // anything the user does to the view stops the film
  const userInput = () => stop();
  for (const type of ['pointerdown', 'wheel', 'touchstart']) canvas.addEventListener(type, userInput, { passive: true });
  addEventListener('keydown', e => { if (running && e.key === 'Escape') stop(); });
  addEventListener('resize', () => { if (running) size(); });
  app.on('frame', onFrame);
  app.on('fly', ({ by }) => { if (by !== 'cinema') stop(); });
  // a mode key (2, 3) during the film: the user takes the view in that mode
  app.on('mode', ({ mode }) => { if (running && mode !== 'orbit') stop({ keepView: true }); });

  return { start, stop: () => stop(), get running() { return running; } };
}
