// Panel wiring, search box, sunlight controls, keyboard shortcuts, help, toasts, photo, share link
// and the loading display. The optional tools (map, labels, tour, measure, hunt) load after the
// first view is up, so a problem in one of them cannot stop the viewer.
import * as THREE from 'three';
import { searchPlaces } from './places.js';
import { decodeView, encodeView } from './permalink.js';
import { compassPoint } from './geo.js';
import { zonedDate, zonedParts } from './sun.js';

const $ = id => document.getElementById(id);
const pad = n => String(n).padStart(2, '0');
const KIND = { building: 'Building', parking: 'Parking', sports: 'Sports', station: 'Station', landmark: 'Landmark' };
const HELP = {
  orbit: { keyboard: 'Drag to orbit · Scroll to zoom · Right-drag to pan', touch: 'Drag to orbit · Pinch to zoom · Two fingers to pan', gamepad: 'Drag to orbit · Scroll to zoom · Right-drag to pan' },
  fly: { keyboard: 'Click the view to look (Esc to release) · W A S D move · Q and E down and up · Shift faster · Scroll changes speed', touch: 'Left thumb moves · Right thumb looks · Up and Down buttons', gamepad: 'Left stick moves · Right stick looks · Bumpers down and up' },
  walk: { keyboard: 'Click the view to look (Esc to release) · W A S D walk · Shift run · Space jump · V changes view', touch: 'Left thumb walks · Right thumb looks · Push the stick to its edge to run', gamepad: 'Left stick walks · Right stick looks · A jumps · B runs' },
};

export function createUI(app) {
  const { camera, controls, canvas } = app;
  const tools = {}; // name -> module API, filled by loadTools()
  const start0 = decodeView(location.hash);

  // ---- toast ----
  let toastTimer = 0;
  function toast(text) {
    const el = $('toast'); el.textContent = text; el.hidden = !text;
    clearTimeout(toastTimer); if (text) toastTimer = setTimeout(() => { el.hidden = true; }, 3200);
  }
  app.on('toast', ({ text }) => toast(text));

  // ---- loading ----
  const mb = b => `${Math.round(b / 1e6)} MB`;
  app.on('progress', p => {
    if (!app.state.ready) {
      const f = p.first ? Math.min(1, p.loaded / p.first) : 0;
      $('load-bar').value = f; $('load-text').textContent = `Loading the campus… ${Math.round(f * 100)}%`;
      return;
    }
    const left = p.total - p.loaded, s = $('stream'), b = $('load-rest'), lite = app.world.budget < Infinity;
    b.hidden = !app.world.paused && !lite; if (!b.hidden) b.textContent = lite ? 'Load everything' : `Load the full campus (${mb(left)})`;
    s.hidden = app.world.paused || !lite && p.tiles >= p.count;
    if (!s.hidden) s.textContent = lite ? 'Lite mode: detail near the view only' : `Loading the rest of the campus · ${Math.round(p.loaded / p.total * 100)}%`;
  });
  app.on('scene:start', ({ manifest }) => {
    $('load').hidden = false; $('error').hidden = true; $('load-bar').value = 0;
    const north = manifest.sources?.north?.saved;
    $('source-snapshot').textContent = manifest.source_saved
      ? `Source snapshot: model saved ${manifest.source_saved}${manifest.source_version ? ` (${manifest.source_version})` : ''}${north ? `; north campus model saved ${north}` : ''}; browser export ${manifest.exported}. Later modelling changes may not appear here yet.`
      : 'Source snapshot: not recorded.';
  });
  app.on('scene:ready', () => {
    $('load').hidden = true;
    if (!applyView(start0)) jump(app.overviewPose());
    loadTools();
  });
  app.on('scene:complete', () => { if (app.world.budget === Infinity) { $('stream').hidden = true; $('load-rest').hidden = true; } });
  // a phone can run out of graphics memory; say so instead of leaving a frozen picture
  canvas.addEventListener('webglcontextlost', e => {
    e.preventDefault(); $('error').hidden = false; $('error-title').textContent = 'The browser ran out of graphics memory';
    $('error-text').textContent = 'Reload to try again in lite mode, which keeps only the part of the campus near the view.';
    $('retry').onclick = () => { const u = new URL(location.href); u.searchParams.set('lite', '1'); u.searchParams.set('quality', 'low'); location.href = u; };
  });
  app.on('scene:error', ({ error }) => { $('load').hidden = true; $('error').hidden = false; $('error-text').textContent = String(error.message || error); });
  app.on('tile:error', ({ tile }) => toast(`Part of the campus did not load (${tile.file}).`));
  $('retry').onclick = () => app.load();
  $('load-rest').onclick = () => {
    if (app.world.paused) { $('load-rest').hidden = true; return app.world.resume(); }
    // leaving lite mode loads about 200 MB: make the user say so twice on a phone
    if ($('load-rest').dataset.armed) { delete $('load-rest').dataset.armed; app.world.loadAll(); }
    else { $('load-rest').dataset.armed = '1'; $('load-rest').textContent = `Tap again to load ${mb(app.world.progress.total)}`; setTimeout(() => { delete $('load-rest').dataset.armed; app.emit('progress', app.world.progress); }, 4000); }
  };

  // through flyTo, so a camera move in progress is cancelled and cannot overwrite the pose on the next frame
  function jump(pose) { app.flyTo(pose, { duration: 0 }); }

  // ---- modes ----
  const setHelp = () => { $('help').textContent = HELP[app.state.mode][app.input.kind] ?? HELP[app.state.mode].keyboard; };
  app.on('mode', ({ mode, view }) => {
    for (const id of ['orbit', 'fly', 'walk']) { $(id).classList.toggle('active', id === mode); $(id).setAttribute('aria-pressed', id === mode); }
    for (const [id, v] of [['view-first', 'first'], ['view-third', 'third']]) { $(id).classList.toggle('active', v === view); $(id).setAttribute('aria-pressed', v === view); }
    $('flight-controls').hidden = mode !== 'fly'; $('walk-controls').hidden = mode !== 'walk';
    document.body.dataset.mode = mode;
    setHelp();
  });
  app.input.onChange(setHelp);
  for (const id of ['orbit', 'fly', 'walk']) $(id).onclick = () => app.setMode(id);
  $('view-first').onclick = () => app.setView('first'); $('view-third').onclick = () => app.setView('third');
  $('jump').onclick = () => app.player.jump(); $('respawn').onclick = () => app.player.respawn();
  $('reset').onclick = () => app.overview(); $('topview').onclick = () => app.topView();
  $('speed').oninput = () => { app.player.flySpeed = +$('speed').value; $('speed-label').textContent = `${$('speed').value} m/s`; };
  app.on('player:speed', ({ speed }) => { $('speed').value = Math.round(speed); $('speed-label').textContent = `${Math.round(speed)} m/s`; });
  app.on('player:status', ({ text }) => { $('walk-status').textContent = text; });
  // double-click in orbit mode: centre the orbit on that spot
  canvas.addEventListener('dblclick', e => {
    if (app.state.mode !== 'orbit' || tools.measure?.active) return;
    const hit = app.world.pick(e.clientX, e.clientY); if (!hit) return;
    const offset = camera.position.clone().sub(controls.target).multiplyScalar(0.6);
    app.flyTo({ position: hit.point.clone().add(offset), target: hit.point }, { duration: 0.9, lift: 0 });
  });

  // ---- quality and stats ----
  $('quality').onchange = e => app.setQuality(e.target.value);
  app.on('quality', ({ name }) => { $('quality').value = name; });
  app.on('stats', ({ fps, triangles, scale }) => {
    const res = scale < 0.99 ? ` · ${Math.round(scale * 100)}% resolution while moving` : '';
    $('performance').textContent = `${fps ? `${fps} fps` : 'idle'} · ${(triangles / 1e6).toFixed(1)} M triangles${res}`;
  });

  // ---- sunlight ----
  const fmtTime = (h, m) => `${h % 12 || 12}:${pad(m)} ${h < 12 ? 'am' : 'pm'}`;
  app.on('sun', ({ azimuth, elevation, date, preset }) => {
    const p = zonedParts(date);
    $('sun-time').value = p.hour * 60 + p.minute; $('sun-date').value = `${p.year}-${pad(p.month)}-${pad(p.day)}`;
    const where = elevation >= 0 ? `sun ${Math.round(elevation)}° up in the ${compassPoint(azimuth)}` : `sun ${Math.round(-elevation)}° below the horizon`;
    $('sun-readout').textContent = `${fmtTime(p.hour, p.minute)} in Montclair · ${where}${preset ? ' · default light' : ''}`;
    $('sun-time').setAttribute('aria-valuetext', `${fmtTime(p.hour, p.minute)}, ${where}`);
  });
  function sunFromInputs() {
    const [year, month, day] = ($('sun-date').value || '2026-09-22').split('-').map(Number), min = +$('sun-time').value;
    if (!year || !month || !day) return;
    app.setTime(zonedDate({ year, month, day, hour: Math.floor(min / 60), minute: min % 60 }));
  }
  $('sun-time').oninput = sunFromInputs; $('sun-date').onchange = sunFromInputs;
  $('sun-now').onclick = () => app.setTime(new Date());
  $('sun-reset').onclick = () => app.resetTime();
  const nudgeSun = minutes => app.setTime(new Date(app.time.date.getTime() + minutes * 60000));

  // ---- search ----
  const box = $('search'), list = $('search-results'); let results = [], cursor = -1;
  function renderResults() {
    list.textContent = '';
    results.forEach(({ place }, i) => {
      const li = document.createElement('li'); li.id = `search-option-${i}`; li.setAttribute('role', 'option'); li.setAttribute('aria-selected', i === cursor);
      const name = document.createElement('span'); name.textContent = place.name;
      const kind = document.createElement('small'); kind.textContent = KIND[place.kind] ?? '';
      li.append(name, kind);
      // select on a finished tap or click, so a swipe that starts on a result scrolls the list instead;
      // holding mousedown keeps focus in the box so the list is not closed before the click lands
      li.onmousedown = e => e.preventDefault(); li.onclick = () => choose(i);
      list.append(li);
    });
    const open = results.length > 0;
    list.hidden = !open; box.setAttribute('aria-expanded', open);
    if (open && cursor >= 0) box.setAttribute('aria-activedescendant', `search-option-${cursor}`); else box.removeAttribute('aria-activedescendant');
  }
  function choose(i) {
    const r = results[i]; if (!r) return;
    box.value = r.place.name; results = []; cursor = -1; renderResults(); box.blur();
    if (!tools.labels?.visible) toast(r.place.name);
    app.goToPlace(r.place);
  }
  box.oninput = () => { results = searchPlaces(app.places, box.value, 8); cursor = results.length ? 0 : -1; renderResults(); };
  box.onkeydown = e => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { if (results.length) { cursor = (cursor + (e.key === 'ArrowDown' ? 1 : -1) + results.length) % results.length; renderResults(); } e.preventDefault(); }
    else if (e.key === 'Enter') { choose(Math.max(0, cursor)); e.preventDefault(); }
    else if (e.key === 'Escape') { box.value = ''; results = []; renderResults(); box.blur(); }
  };
  // close a moment after focus leaves, so a tap that moved focus still reaches its result
  box.onblur = () => setTimeout(() => { if (document.activeElement !== box && results.length) { results = []; renderResults(); } }, 200);
  box.onfocus = () => { if (box.value) box.oninput(); };

  // ---- share link and permalink ----
  function currentView() {
    const p = app.time.preset ? null : zonedParts(app.time.date);
    const target = app.state.mode === 'orbit' ? controls.target : camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(20).add(camera.position);
    // in walk mode the link holds the walker's eye, not the third-person camera behind them
    const eye = app.state.mode === 'walk' && app.player.placed ? app.player.position.clone().setY(app.player.position.y + 1.65) : camera.position;
    return {
      mode: app.state.mode, position: eye.toArray(), target: target.toArray(),
      time: p ? `${p.year}-${pad(p.month)}-${pad(p.day)}T${pad(p.hour)}:${pad(p.minute)}` : null,
      labels: !!tools.labels?.visible,
    };
  }
  let hashTimer = 0, wantLabels; // label setting from a link, held until the labels tool has loaded
  const writeHash = () => { if (app.state.ready) history.replaceState(null, '', `#${encodeView(currentView())}`); };
  const scheduleHash = () => { clearTimeout(hashTimer); hashTimer = setTimeout(writeHash, 700); };
  app.on('camera', scheduleHash); app.on('sun', scheduleHash); app.on('mode', scheduleHash); app.on('labels', scheduleHash);
  /** Restore a decoded permalink. Returns false when it holds no camera pose. */
  function applyView(v) {
    if (!v) return false;
    if (v.time) { const m = /^(\d+)-(\d+)-(\d+)T(\d+):(\d+)$/.exec(v.time); if (m) app.setTime(zonedDate({ year: +m[1], month: +m[2], day: +m[3], hour: +m[4], minute: +m[5] })); }
    if (!v.position || !v.target) return false;
    const position = new THREE.Vector3(...v.position), target = new THREE.Vector3(...v.target);
    if (position.distanceTo(target) < 0.5) return false;
    // a link with no time was saved under the default light: go back to it if the sun has been moved since
    if (!v.time && !app.time.preset) app.resetTime();
    // go through orbit so the pose is not overwritten by the fly or walk controller on the next frame
    if (app.state.mode !== 'orbit') app.setMode('orbit');
    if (v.mode === 'fly' || v.mode === 'walk') {
      // set the pose directly: the orbit controls would clamp an upward look and move the camera
      app.cancelFly(); camera.position.copy(position); controls.target.copy(target); camera.lookAt(target); app.invalidate();
      if (v.mode === 'fly') app.setMode('fly');
      else app.setMode('walk', { at: position.clone().setY(position.y - 1.65) });
    } else jump({ position, target });
    if (typeof v.labels === 'boolean') {
      if (tools.labels) { if (tools.labels.visible !== v.labels) tools.labels.setVisible(v.labels); wantLabels = undefined; }
      else wantLabels = v.labels;
    }
    return true;
  }
  addEventListener('hashchange', () => applyView(decodeView(location.hash)));
  async function share() {
    writeHash();
    try { await navigator.clipboard.writeText(location.href); toast('Link to this view copied.'); }
    catch { toast('Copy the address bar to share this view.'); }
  }

  // ---- photo ----
  function photo() {
    app.look.update(app.state.mode === 'orbit' ? controls.target : null, true); app.look.render(false);
    const w = canvas.width, h = canvas.height, out = document.createElement('canvas'); out.width = w; out.height = h;
    const g = out.getContext('2d'); g.drawImage(canvas, 0, 0); // same task as the draw, so the buffer is still there
    const size = Math.max(12, Math.round(h / 60)), text = 'Montclair State campus · working model, not a survey · Map data © OpenStreetMap contributors';
    g.font = `${size}px system-ui, sans-serif`; g.textBaseline = 'bottom';
    g.fillStyle = 'rgba(0,0,0,.45)'; g.fillRect(0, h - size * 1.9, g.measureText(text).width + size * 1.6, size * 1.9);
    g.fillStyle = '#fff'; g.fillText(text, size * 0.8, h - size * 0.45);
    out.toBlob(blob => {
      if (!blob) return toast('Could not save the picture.');
      const d = new Date(), a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = `montclair-campus-${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}.png`;
      a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 5000); toast('Picture saved.');
    }, 'image/png');
  }

  // ---- tools ----
  const press = (id, on) => { $(id).setAttribute('aria-pressed', !!on); $(id).classList.toggle('active', !!on); };
  const toggles = {
    labels: () => tools.labels?.setVisible(!tools.labels.visible),
    map: () => tools.hud?.setMap(!tools.hud.map),
    measure: () => { if (!tools.measure) return; if (!tools.measure.active) { tools.tour?.stop(); if (app.state.mode !== 'orbit') app.setMode('orbit'); } tools.measure.setActive(!tools.measure.active); },
    tour: () => { if (!tools.tour) return; if (tools.tour.running) tools.tour.stop(); else { tools.measure?.setActive(false); if (app.state.mode !== 'orbit') app.setMode('orbit'); tools.tour.start(); } },
    hunt: () => { if (!tools.hunt) return; if (tools.hunt.active) tools.hunt.stop(); else tools.hunt.start(); },
    photo, share,
    help: () => { const d = $('help-dialog'); if (d.open) d.close(); else d.showModal(); },
  };
  for (const name of Object.keys(toggles)) $(`tool-${name}`).onclick = toggles[name];
  app.on('labels', ({ on }) => press('tool-labels', on));
  app.on('hud:map', ({ on }) => press('tool-map', on));
  app.on('measure', ({ active }) => press('tool-measure', active));
  app.on('tour', ({ running }) => press('tool-tour', running));
  app.on('hunt', ({ active }) => press('tool-hunt', active));

  async function loadTools() {
    if (tools.loading) return; tools.loading = true;
    const load = async (name, module, factory) => {
      try { tools[name] = (await module)[factory](app); }
      catch (e) { console.error(`${name} tool failed to start`, e); $(`tool-${name === 'hud' ? 'map' : name}`).disabled = true; }
    };
    await Promise.all([
      load('hud', import('./hud.js'), 'createHud'), load('labels', import('./labels.js'), 'createLabels'), load('tour', import('./tour.js'), 'createTour'),
      load('measure', import('./measure.js'), 'createMeasure'), load('hunt', import('./hunt.js'), 'createHunt'),
    ]);
    press('tool-labels', tools.labels?.visible); press('tool-map', tools.hud?.map);
    if (wantLabels !== undefined && tools.labels && tools.labels.visible !== wantLabels) tools.labels.setVisible(wantLabels);
    wantLabels = undefined;
    press('tool-hunt', tools.hunt?.active);
  }

  // ---- panel: open on a desktop, a drop-down sheet on a phone ----
  const narrow = matchMedia('(max-width: 700px), (max-height: 520px)');
  function setPanel(open) { $('panel').hidden = !open; $('panel-toggle').setAttribute('aria-expanded', open); $('panel-toggle').classList.toggle('active', open && narrow.matches); }
  $('panel-toggle').onclick = () => setPanel($('panel').hidden);
  // on a phone the mode switch lives in the top bar, where a thumb can reach it without opening the sheet
  function layout() { (narrow.matches ? $('mode-slot') : $('panel-body')).prepend($('mode-group')); setPanel(!narrow.matches); }
  layout(); narrow.addEventListener('change', layout);
  canvas.addEventListener('pointerdown', () => { if (narrow.matches) setPanel(false); });
  app.on('mode', ({ mode }) => { if (narrow.matches && mode !== 'orbit') setPanel(false); });
  // other cards sit below the top bar, whatever height it wraps to
  new ResizeObserver(() => document.documentElement.style.setProperty('--top-h', `${Math.round($('top').getBoundingClientRect().bottom)}px`)).observe($('top'));

  // ---- full screen ----
  const root = document.documentElement;
  const canFull = !!(root.requestFullscreen || root.webkitRequestFullscreen) && (document.fullscreenEnabled ?? document.webkitFullscreenEnabled ?? true);
  const isFull = () => !!(document.fullscreenElement || document.webkitFullscreenElement) || document.body.classList.contains('immersive');
  function showFull() { const on = isFull(); $('fullscreen').setAttribute('aria-pressed', on); $('immersive-exit').hidden = !document.body.classList.contains('immersive'); }
  /** Browser full screen where it exists. iPhone Safari has none, so there we hide the interface instead. */
  async function fullscreen() {
    if (canFull) {
      try {
        if (document.fullscreenElement || document.webkitFullscreenElement) await (document.exitFullscreen ?? document.webkitExitFullscreen).call(document);
        else await (root.requestFullscreen ?? root.webkitRequestFullscreen).call(root, { navigationUI: 'hide' });
        return;
      } catch { /* refused: fall through to hiding the interface */ }
    }
    const on = document.body.classList.toggle('immersive');
    if (on && !matchMedia('(display-mode: fullscreen), (display-mode: standalone)').matches) toast('Interface hidden. For true full screen, add this page to your Home Screen.');
    showFull();
  }
  $('fullscreen').onclick = fullscreen; $('immersive-exit').onclick = fullscreen;
  for (const type of ['fullscreenchange', 'webkitfullscreenchange']) document.addEventListener(type, showFull);

  // ---- keyboard shortcuts ----
  const KEYS = {
    Digit1: () => app.setMode('orbit'), Digit2: () => app.setMode('fly'), Digit3: () => app.setMode('walk'),
    KeyO: () => app.overview(), KeyT: () => app.topView(), KeyL: toggles.labels, KeyM: toggles.map, KeyR: toggles.measure,
    KeyG: toggles.tour, KeyH: toggles.hunt, KeyP: photo, KeyK: share, KeyF: fullscreen,
    KeyV: () => { if (app.state.mode === 'walk') app.setView(app.state.view === 'first' ? 'third' : 'first'); },
    BracketLeft: () => nudgeSun(-15), BracketRight: () => nudgeSun(15),
    Slash: e => { if (e.shiftKey) toggles.help(); else { if (document.pointerLockElement) document.exitPointerLock(); box.focus(); box.select(); } },
  };
  addEventListener('keydown', e => {
    if (e.ctrlKey || e.metaKey || e.altKey || e.repeat && !e.code.startsWith('Bracket')) return;
    const t = e.target;
    if (t instanceof HTMLElement && (t.isContentEditable || ['INPUT', 'SELECT', 'TEXTAREA'].includes(t.tagName))) return;
    if ($('help-dialog').open) return;
    const fn = KEYS[e.code]; if (!fn) return;
    fn(e); e.preventDefault();
  });

  return {
    tools,
    start() {
      setHelp();
      app.emit('mode', { mode: app.state.mode, view: app.state.view });
      app.load({ view: start0 });
    },
  };
}
