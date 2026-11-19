// Landmark hunt: walk or fly to nine campus landmarks to tag them. Made for walk mode; fly works
// too. In orbit mode nothing is tagged, because hovering the orbit centre over a place is not a visit.
// Progress is kept in localStorage so a reload carries on where you left off.
import { selectTargets, isFound, nearestTarget, arrowAngle, horizontalDistance, formatElapsed, parseProgress } from './hunt-math.js';

const KEY = 'campus-hunt';
const CHECK_MS = 250; // found test at most 4 times a second
const CONFETTI = 32, CONFETTI_MS = 2000;
const COLOURS = ['#b3282d', '#ffffff', '#d4a531'];

/**
 * Create the hunt. Returns { start(), stop(), reset(), active, found, dispose() }.
 * `found` is the list of tagged target names. Emits `hunt` { active, found, total } on changes,
 * where `found` and `total` are counts.
 */
export function createHunt(app) {
  const overlay = document.getElementById('overlay') || document.body;
  const calm = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  let targets = [], found = new Set(), start = null, end = null;
  let active = false, lastCheck = 0, timer = 0, offs = [];
  const rows = new Map();

  // ---- DOM ----
  const card = el('section', 'hunt-card'); card.hidden = true;
  card.setAttribute('aria-label', 'Landmark hunt');
  const head = el('div', 'hunt-head');
  const toggle = el('button', 'hunt-toggle'); toggle.type = 'button';
  toggle.setAttribute('aria-controls', 'hunt-body');
  const count = el('span', 'hunt-count');
  const arrow = el('span', 'hunt-arrow'); arrow.setAttribute('aria-hidden', 'true');
  arrow.innerHTML = '<svg viewBox="0 0 16 16" width="16" height="16"><path d="M8 1.5 13.5 13 8 10.2 2.5 13Z" fill="currentColor"/></svg>';
  const next = el('span', 'hunt-next');
  const chevron = el('span', 'hunt-chevron'); chevron.setAttribute('aria-hidden', 'true');
  toggle.append(count, arrow, next, chevron);
  const close = el('button', 'hunt-close', '×'); close.type = 'button';
  close.setAttribute('aria-label', 'Close the hunt'); close.title = 'Close the hunt (progress is kept)';
  close.addEventListener('click', () => stop());
  head.append(toggle, close);
  const hint = el('p', 'hunt-hint', 'Walk or fly there to tag it');
  const body = el('div', 'hunt-body'); body.id = 'hunt-body';
  const intro = el('p', 'hunt-intro', 'Walk or fly to each landmark to tag it.');
  const list = el('ul', 'hunt-list');
  const done = el('div', 'hunt-done'); done.hidden = true;
  const doneTitle = el('p', 'hunt-done-title', 'You found them all');
  const doneTime = el('p', 'hunt-done-time');
  const again = el('button', 'hunt-again', 'Play again'); again.type = 'button';
  again.addEventListener('click', () => reset());
  done.append(doneTitle, doneTime, again);
  body.append(intro, list, done);
  card.append(head, hint, body);
  overlay.append(card);
  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  setOpen(!matchMedia('(max-width: 700px), (max-height: 520px)').matches);

  function el(tag, cls, text) {
    const e = document.createElement(tag); e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function setOpen(open) {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', `Landmark hunt, ${count.textContent}. ${open ? 'Hide' : 'Show'} the list`);
    body.hidden = !open;
  }

  /** One list row per target. Found rows are buttons that fly there; the rest show a distance. */
  function buildList() {
    list.replaceChildren(); rows.clear();
    for (const t of targets) {
      const li = el('li', 'hunt-item');
      const row = el('button', 'hunt-row'); row.type = 'button';
      const mark = el('span', 'hunt-mark'); mark.setAttribute('aria-hidden', 'true');
      const name = el('span', 'hunt-name', t.label);
      const dist = el('span', 'hunt-dist');
      row.append(mark, name, dist);
      row.addEventListener('click', () => { if (found.has(t.name)) app.goToPlace(t); });
      li.append(row); list.append(li);
      rows.set(t.name, { li, row, dist, t });
    }
  }

  // ---- state ----
  function load() {
    let saved = { found: [], start: null, end: null };
    try { saved = parseProgress(localStorage.getItem(KEY)); } catch { /* storage blocked */ }
    found = new Set(saved.found); start = saved.start; end = saved.end;
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify({ found: [...found], start, end })); } catch { /* storage blocked or full */ }
  }
  const foundCount = () => targets.filter(t => found.has(t.name)).length;
  const complete = () => targets.length > 0 && foundCount() === targets.length;
  function emit() { app.emit('hunt', { active, found: foundCount(), total: targets.length }); }

  function setTargets() {
    targets = selectTargets(app.places || []);
    buildList(); refresh(); emit();
  }

  /** Where the player is: walk and fly count, orbit only points (from the orbit centre). */
  function whereAmI() {
    const mode = app.state.mode;
    // entering walk mode: the mode event comes before the walker is placed, and the old position must not tag anything
    if (mode === 'walk') return app.player.placed ? { pos: app.player.position, counts: true } : { pos: app.camera.position, counts: false };
    if (mode === 'fly') return { pos: app.camera.position, counts: true };
    return { pos: app.controls.target, counts: false };
  }

  /** Update everything that does not move with the camera. */
  function refresh() {
    const n = foundCount(), all = complete();
    count.textContent = all ? `All ${targets.length} found` : `${n} of ${targets.length}`;
    for (const { li, row, t } of rows.values()) {
      const got = found.has(t.name);
      li.classList.toggle('hunt-found', got);
      row.setAttribute('aria-disabled', String(!got));
      row.title = got ? `Go to ${t.label}` : 'Not found yet';
    }
    done.hidden = !all;
    if (all) doneTime.textContent = start && end ? `Time: ${formatElapsed(end - start)}` : '';
    hint.hidden = all || app.state.mode !== 'orbit';
    setOpen(toggle.getAttribute('aria-expanded') === 'true'); // keeps the accessible name current
    point();
  }

  /** Pointer to the nearest unfound target. Cheap; runs on every camera event. */
  function point() {
    const { pos } = whereAmI();
    const near = nearestTarget(targets, found, pos);
    arrow.hidden = !near;
    if (!near) {
      next.textContent = complete() && start && end ? formatElapsed(end - start) : '';
      return;
    }
    arrow.style.transform = `rotate(${arrowAngle(pos, near.target, app.heading()).toFixed(1)}deg)`;
    next.textContent = `${near.target.label} · ${Math.round(near.distance)} m`;
  }

  /** Found test and row distances, throttled. */
  function check() {
    lastCheck = performance.now(); clearTimeout(timer); timer = 0;
    const { pos, counts } = whereAmI();
    const fresh = counts ? targets.filter(t => !found.has(t.name) && isFound(t, pos)) : [];
    for (const { dist, t } of rows.values()) dist.textContent = found.has(t.name) ? '' : `${Math.round(horizontalDistance(pos, t))} m`;
    if (!fresh.length) return;
    for (const t of fresh) found.add(t.name);
    if (complete()) end = Date.now();
    save(); refresh(); emit();
    for (const t of fresh) celebrate(t);
  }
  function onCamera() {
    if (!active) return;
    point();
    const wait = CHECK_MS - (performance.now() - lastCheck);
    if (wait <= 0) check();
    else if (!timer) timer = setTimeout(check, wait); // trailing check so the last position counts
  }

  // ---- feedback ----
  function celebrate(t) {
    app.toast(`Found: ${t.label}`);
    const r = rows.get(t.name);
    if (r) {
      r.li.classList.remove('hunt-pop'); void r.li.offsetWidth; // restart the animation
      r.li.classList.add('hunt-pop');
      setTimeout(() => r.li.classList.remove('hunt-pop'), 900);
    }
    if (calm()) return;
    const box = (r && !body.hidden ? r.li : card).getBoundingClientRect();
    confetti(box.left + Math.min(box.width / 2, 120), box.top + box.height / 2);
  }
  function confetti(x, y) {
    const burst = el('div', 'hunt-confetti');
    burst.style.left = `${x}px`; burst.style.top = `${y}px`;
    for (let i = 0; i < CONFETTI; i++) {
      const p = el('i', 'hunt-bit');
      const a = (i / CONFETTI) * Math.PI * 2 + Math.random() * 0.4, d = 40 + Math.random() * 70;
      p.style.setProperty('--dx', `${(Math.cos(a) * d).toFixed(1)}px`);
      p.style.setProperty('--dy', `${(Math.sin(a) * d - 30).toFixed(1)}px`);
      p.style.setProperty('--r', `${Math.round(Math.random() * 720 - 360)}deg`);
      p.style.background = COLOURS[i % COLOURS.length];
      p.style.animationDelay = `${Math.round(Math.random() * 120)}ms`;
      burst.append(p);
    }
    overlay.append(burst);
    setTimeout(() => burst.remove(), CONFETTI_MS);
  }

  // ---- API ----
  /** Show the hunt and start tagging. Picks up saved progress. */
  function startHunt() {
    if (active) return;
    active = true; load();
    if (!start) { start = Date.now(); save(); }
    card.hidden = false;
    offs = [
      app.on('camera', onCamera),
      app.on('places', setTargets),
      app.on('mode', () => { refresh(); check(); }),
    ];
    setTargets(); check();
  }
  /** Hide the hunt. Progress is kept. */
  function stop() {
    if (!active) return;
    active = false; card.hidden = true;
    clearTimeout(timer); timer = 0;
    offs.forEach(off => off()); offs = [];
    emit();
  }
  /** Forget all progress and start the clock again. */
  function reset() {
    try { localStorage.removeItem(KEY); } catch { /* storage blocked */ }
    found = new Set(); end = null; start = active ? Date.now() : null;
    if (active) save();
    refresh(); emit();
    if (active) check();
  }

  return {
    start: startHunt, stop, reset,
    get active() { return active; },
    get found() { return targets.filter(t => found.has(t.name)).map(t => t.name); },
    get total() { return targets.length; },
    dispose() { stop(); card.remove(); },
  };
}
