// Walking directions in walk mode: pick a building or place, get a route along the campus paths to its
// entrance (viewer/paths.json, A* in route-math.js). Starts from the walker: the GPS position when
// follow me is on, else wherever they stand in the model. viewer/nav.js draws the route and guides.
import { searchPlaces } from './places.js';
import { parsePaths, route as findRoute, walkMinutes } from './route-math.js';

/** Builds the destination picker. Returns { go(place), clear(), get current }. Emits `route` with { route, place, stepFree } or null. */
export function createRoute(app) {
  const { player } = app;
  const box = document.querySelector('.follow') ?? document.getElementById('overlay');
  const open = document.createElement('button');
  open.type = 'button'; open.className = 'follow-btn route-open'; open.setAttribute('aria-expanded', 'false');
  open.innerHTML = '<span class="follow-main">Go to a place</span><span class="follow-note">Walking directions</span>';
  const pick = document.createElement('div'); pick.className = 'route-pick'; pick.hidden = true;
  pick.innerHTML = `<div class="route-row"><input type="search" class="route-search" placeholder="Building or place" autocomplete="off" spellcheck="false" aria-label="Where to">
    <button type="button" class="route-close" aria-label="Close">×</button></div>
    <label class="route-free"><input type="checkbox" class="route-stepfree"> Step-free (no stairs or steep slopes)</label>
    <ul class="route-results" role="listbox" aria-label="Places"></ul>`;
  const card = document.createElement('div'); card.className = 'route-card'; card.hidden = true; card.setAttribute('aria-live', 'polite');
  box.append(open, pick, card);
  const input = pick.querySelector('.route-search'), list = pick.querySelector('.route-results'), free = pick.querySelector('.route-stepfree');

  let graph = null, loading = null, current = null, ask = 0;
  // a failed fetch is not kept, so the next try fetches again
  const loadGraph = () => loading ??= fetch('./viewer/paths.json').then(r => r.json()).then(j => (graph = parsePaths(j)))
    .catch(() => { loading = null; return (graph = null); });

  function showPick(on) {
    pick.hidden = !on; open.setAttribute('aria-expanded', on);
    if (on) { loadGraph(); input.value = ''; list.replaceChildren(); input.focus(); }
  }
  open.onclick = () => showPick(pick.hidden);
  pick.querySelector('.route-close').onclick = () => showPick(false);
  input.oninput = () => {
    const hits = searchPlaces(app.places ?? [], input.value, 6);
    list.replaceChildren(...hits.map(({ place }) => {
      const li = document.createElement('li'); li.setAttribute('role', 'option');
      const b = document.createElement('button'); b.type = 'button'; b.textContent = place.name;
      b.onclick = () => { showPick(false); go(place); };
      li.append(b); return li;
    }));
  };
  input.onkeydown = e => { if (e.key === 'Enter') list.querySelector('button')?.click(); if (e.key === 'Escape') showPick(false); };

  function describe() {
    const { route: r, place, stepFree } = current;
    const notes = [];
    if (!r.goal.mapped) notes.push('Entrance guessed from the path map (UNVERIFIED)');
    if (r.steps) notes.push('Has stairs');
    if (r.steep) notes.push('Has steep stretches');
    if (stepFree) notes.push('Step-free');
    if (r.offPath > 8) notes.push(`Starts at the nearest ${stepFree ? 'step-free ' : ''}path, ${Math.round(r.offPath)} m from you`);
    card.replaceChildren(
      text(`To ${place.name}`, 'route-to'),
      text(`${Math.round(r.length)} m · ${walkMinutes(r.length)} min walk`, 'route-len'),
      ...(notes.length ? [text(notes.join(' · '), 'route-notes')] : []),
      clearButton(),
    );
  }
  function text(t, cls = '') { const s = document.createElement('span'); s.className = cls; s.textContent = t; return s; }
  function clearButton() { const b = document.createElement('button'); b.type = 'button'; b.className = 'route-clear'; b.textContent = 'Clear route'; b.onclick = clear; return b; }

  /** Route from the walker to `place`. Resolves the route, or null when there is none. */
  async function go(place, { stepFree = free.checked } = {}) {
    const my = ++ask;
    await loadGraph();
    // the walker's position is stale until walk mode has put them on the ground
    while (!player.guide && (!player.placed || player.busy) && my === ask && app.state.mode === 'walk') await new Promise(r => setTimeout(r, 150));
    if (my !== ask) return null; // cleared, or left walk mode, while the map loaded or the walker landed
    if (!graph) { app.toast('The path map did not load.'); return null; }
    const from = player.guide ?? player.position;
    const r = findRoute(graph, { x: from.x, z: from.z }, place, { stepFree });
    if (!r) {
      current = null;
      const none = stepFree ? `No step-free route to ${place.name} on the path map.` : `No route to ${place.name}: you are away from the campus paths.`;
      card.hidden = false; card.replaceChildren(text(none), clearButton());
      app.emit('route', null); return null;
    }
    current = { route: r, place, stepFree };
    describe(); card.hidden = false;
    app.emit('route', current);
    return r;
  }

  function clear() {
    ask++; current = null; card.hidden = true; card.replaceChildren(); app.emit('route', null);
  }

  app.on('mode', ({ mode }) => { if (mode !== 'walk') { showPick(false); clear(); } });

  return { go, clear, get current() { return current; }, get graph() { return graph; }, loadGraph };
}
