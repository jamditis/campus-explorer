// Capture the teaser frame by frame from the viewer in headless Chromium (software WebGL).
//   node tools/teaser/capture.mjs OUT_DIR [--fonts DIR] [--quality high] [--width 1920 --height 1080]
//        [--step N] [--only shot,shot] [--from FRAME] [--to FRAME] [--sub N] [--site FROZEN_COPY]
// Writes OUT_DIR/frames/NNNNN.png (raw, no grade). Frames already on disk are skipped, so a run that
// stopped (or a tab that crashed) carries on from where it was. `--step 6` shoots every 6th frame (an
// animatic); `--sub 3` averages 3 sub-frames per frame on shots with `blur: true` (motion blur).
// The camera, the time of day, the interface fade and the 3D graphics all come from storyboard.mjs.
import { existsSync, mkdirSync, readFileSync, renameSync, appendFileSync, writeFileSync, copyFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { open, serve, waitFor } from '../viewer-test/lib.mjs';
import { installSettle, settle } from './page.mjs';
import { installGraphics } from './graphics.mjs';
import { cameraAt, frameAt, presence, timeAt, timeline } from './path.mjs';
import { storyboard } from './storyboard.mjs';

const here = dirname(fileURLToPath(import.meta.url)), repo = resolve(here, '../..');
const argv = process.argv.slice(2), out = resolve(argv[0] ?? '');
if (!argv[0] || argv[0].startsWith('--')) { console.error('usage: capture.mjs OUT_DIR [options]'); process.exit(2); }
const opt = (name, d) => { const i = argv.indexOf(`--${name}`); return i > 0 ? argv[i + 1] : d; };
const width = +opt('width', storyboard.width), height = +opt('height', storyboard.height);
const step = +opt('step', 1), sub = +opt('sub', 1), quality = opt('quality', 'high');
const only = opt('only', '') ? opt('only').split(',') : null;
const fontDir = resolve(opt('fonts', join(out, 'fonts')));
const { fps, shots } = storyboard;
const { starts, frames } = timeline(shots, fps);
const from = +opt('from', 0), to = Math.min(frames, +opt('to', frames));
const framesDir = join(out, 'frames'); mkdirSync(framesDir, { recursive: true });
const logFile = join(out, 'capture.log');
const log = s => { console.log(s); appendFileSync(logFile, `${new Date().toISOString()} ${s}\n`); };
if (repo === out || out.startsWith(repo + '/')) { console.error('write the frames outside the repository'); process.exit(2); }

// letter outlines: made once from the machine's Inter Display (tools/teaser/font.py)
const fonts = {};
for (const [name, file] of [['semibold', 'InterDisplay-SemiBold.otf'], ['regular', 'InterDisplay-Regular.otf']]) {
  const json = join(fontDir, `${name}.json`);
  if (!existsSync(json)) {
    mkdirSync(fontDir, { recursive: true });
    const r = spawnSync('python3', [join(here, 'font.py'), `/usr/share/fonts/opentype/inter/${file}`, json], { stdio: 'inherit' });
    if (r.status) process.exit(r.status);
  }
  fonts[name] = JSON.parse(readFileSync(json, 'utf8'));
}
// the finish pass (finish.py) reads the grade and the film look per frame from plan.json
const plan = { fps, grades: storyboard.grades, frames: [], shots: shots.map((s, i) => ({ name: s.name, start: starts[i] })) };
for (let f = 0; f < frames; f++) {
  const at = frameAt(f, shots, fps), shot = shots[at.shot], film = shot.film ? shot.film(at.sec) : 1;
  plan.frames.push({ shot: at.shot, grade: shot.grade ?? 'day', film, bars: shot.bars ? shot.bars(at.sec) : film });
}
writeFileSync(join(out, 'plan.json'), JSON.stringify(plan));
const mathSource = readFileSync(join(here, 'path.mjs'), 'utf8').replace(/^export /gm, '');

const todo = [];
for (let f = from; f < to; f++) {
  const at = frameAt(f, shots, fps);
  if (only && !only.includes(shots[at.shot].name)) continue;
  if (shots[at.shot].still && f !== starts[at.shot]) continue;
  if ((f - starts[at.shot]) % step && f !== starts[at.shot] + Math.round(shots[at.shot].duration * fps) - 1) continue;
  if (!existsSync(join(framesDir, `${String(f).padStart(5, '0')}.png`))) todo.push(f);
}
log(`${todo.length} frames to shoot of ${frames} (${width}x${height}, ${quality}, step ${step}, sub ${sub})`);
if (!todo.length) process.exit(0);

// --site DIR: serve a frozen copy of the viewer and its models, so a new export cannot change the film
const site = resolve(opt('site', repo));
const server = await serve(site);
log(`serving ${site}`);
let browser = null, page = null, built = -1;
async function start() {
  if (browser) await browser.close().catch(() => {});
  const t0 = Date.now();
  ({ browser, page } = await open(`${server.url}?capture&quality=${quality}`, { width, height, minutes: 90 }));
  // draw nothing while the campus streams in (each software draw holds the page for half a minute)
  await waitFor(page, 'ready');
  await installSettle(page);
  await waitFor(page, 'loaded');
  // far versions of tiles load after the campus: wait for all of them (else they swap in mid-shot)
  const want = await page.evaluate(() => fetch('models/main/manifest.json').then(r => r.json()).then(m => m.tiles.filter(t => t.lod).length));
  let n = 0;
  for (let i = 0, last = -1, same = 0; i < 240 && n < want && same < 24; i++) {
    await page.waitForTimeout(5000); n = await page.evaluate(() => window.__campus.lods);
    same = n === last ? same + 1 : 0; last = n; // two minutes with no new far version: the rest have none
  }
  // the frame-rate readout would show the capture's own numbers (one draw per frame, none in between)
  await page.addStyleTag({ content: 'body.teaser-noui>:not(#viewer){display:none!important}.teaser-fade>:not(#viewer){transition:none!important}#performance{visibility:hidden}' });
  // the visitor closes the minimap (a real click on Map); in software WebGL it is drawn too late to read
  if (await page.locator('#tool-map[aria-pressed=true]').count()) await page.click('#tool-map');
  await page.evaluate(installGraphics, { fonts, mathSource });
  built = -1;
  log(`viewer loaded in ${((Date.now() - t0) / 1000).toFixed(0)} s, ${n} of ${want} far versions`);
}

/** Resolve storyboard heights: [x, h, z] with `rel` are metres above the ground at (x, z). */
async function ground(shot) {
  if (shot._abs) return shot._abs;
  const up = async list => page.evaluate(({ list, rel }) => list.map(([x, y, z]) => [x, rel ? y + (window.__campus.groundAt(x, z) ?? 100) : y, z]), { list, rel: !!shot.rel });
  const g = [];
  const upg = async (list, rel) => page.evaluate(({ list, rel }) => list.map(([x, y, z]) => [x, rel ? y + (window.__campus.groundAt(x, z) ?? 100) : y, z]), { list, rel });
  for (const d of shot.graphics ?? []) {
    const e = { ...d }, rel = d.rel ?? !!shot.rel; // a graphic may set its own `rel`
    if (e.at) [e.at] = await upg([e.at], rel);
    if (e.a) [e.a, e.b] = await upg([e.a, e.b], rel);
    g.push(e);
  }
  const shadow = shot.shadow ? { focus: (await up([shot.shadow.focus]))[0], half: shot.shadow.half } : null;
  shot._abs = { ...shot, graphics: g, shadow };
  if (!shot.move) { shot._abs.pos = await up(shot.pos); shot._abs.look = await up(shot.look); }
  return shot._abs;
}

/** Type into the viewer's search box with the real keyboard, up to the text the storyboard wants now. */
async function type(want) {
  const box = page.locator('#search');
  const have = await box.inputValue();
  if (want === have) return;
  if (!want.startsWith(have)) { await box.fill(''); }
  await box.focus();
  await page.keyboard.type(want.slice(want.startsWith(have) ? have.length : 0));
}

async function build(i) {
  if (built === i) return;
  const s = await ground(shots[i]);
  await page.evaluate(gs => {
    const G = window.__teaser.graphics; G.clear();
    for (const g of gs) (g.kind === 'text' ? G.addText : g.kind === 'dim' ? G.addDimension : G.addPin)(g);
  }, s.graphics);
  built = i;
}

/** What decides a frame's picture; two frames with the same signature are the same image. */
function signature(f) {
  const at = frameAt(f, shots, fps), shot = shots[at.shot], sec = at.sec;
  const g = (shot.graphics ?? []).map(d => { const p = presence(d, sec); return [d.id, +p.up.toFixed(4), +p.down.toFixed(4)]; });
  return JSON.stringify([at.shot, cameraAt(shot.move ? shot : { ...shot, pos: shot.pos, look: shot.look }, at.t),
    shot.time ? timeAt(shot, at.t).getTime() : 0, g, shot.ui ? +shot.ui(sec).toFixed(4) : 0, shot.typed ? shot.typed(sec) : '']);
}

async function shoot(f) {
  const at = frameAt(f, shots, fps), shot = shots[at.shot];
  // a held frame (nothing moves: the interface bookends) is a copy of the frame before it
  const prev = join(framesDir, `${String(f - 1).padStart(5, '0')}.png`);
  if (f > 0 && existsSync(prev) && signature(f) === signature(f - 1)) {
    copyFileSync(prev, join(framesDir, `${String(f).padStart(5, '0')}.png`));
    return;
  }
  await build(at.shot);
  const s = shot._abs, n = Math.round(shot.duration * fps);
  const subs = shot.blur && sub > 1 ? sub : 1, paths = [];
  for (let k = 0; k < subs; k++) {
    // sub-frames spread over half a frame (a 180° shutter), centred on the frame time
    const local = subs > 1 ? at.t + ((k + 0.5) / subs - 0.5) * 0.5 / Math.max(1, n - 1) : at.t;
    const sec = local * shot.duration, cam = cameraAt(s, local);
    const states = {};
    for (const g of s.graphics) states[g.id] = presence(g, sec);
    const ui = shot.ui ? shot.ui(sec) : 0; // interface opacity 0..1
    await page.evaluate(({ cam, time, states, ui, shadow }) => {
      const T = window.__teaser;
      document.body.classList.toggle('teaser-noui', ui <= 0);
      document.body.classList.add('teaser-fade');
      for (const el of document.body.children) if (el.id !== 'viewer') el.style.opacity = ui > 0 && ui < 1 ? String(ui) : '';
      T.graphics.pose(states);
      T.shot({ pose: [...cam.pos, ...cam.look], fov: cam.fov, time, shadow });
    }, { cam, time: shot.time ? timeAt(shot, local).toISOString() : null, states, ui, shadow: s.shadow ?? null });
    if (shot.typed && k === 0) await type(shot.typed(sec));
    await settle(page);
    // the viewer shows "ran out of graphics memory" when the WebGL context is lost: never keep such a frame
    if (await page.evaluate(() => window.__campus.app.renderer.getContext().isContextLost())) throw new Error('WebGL context lost');
    const p = join(framesDir, subs > 1 ? `${String(f).padStart(5, '0')}.s${k}.png` : `${String(f).padStart(5, '0')}.tmp.png`);
    await page.screenshot({ path: p });
    paths.push(p);
  }
  const final = join(framesDir, `${String(f).padStart(5, '0')}.png`);
  if (subs > 1) {
    const r = spawnSync('python3', [join(here, 'blend.py'), final, ...paths], { stdio: 'inherit' });
    if (r.status) throw new Error('sub-frame blend failed');
  } else renameSync(paths[0], final);
}

await start();
let done = 0, t0 = Date.now(), crashes = 0;
for (let i = 0; i < todo.length;) {
  try {
    await shoot(todo[i]); i++; done++;
    if (done % 200 === 0 && i < todo.length) { log('fresh tab (memory)'); await start(); } // a long run leaks memory
    if (done % 10 === 0 || i === todo.length) {
      const per = (Date.now() - t0) / 1000 / done;
      log(`frame ${todo[i - 1]} (${i}/${todo.length}) ${per.toFixed(1)} s per frame, ${((todo.length - i) * per / 60).toFixed(0)} min left`);
    }
  } catch (e) {
    log(`frame ${todo[i]} failed: ${e.message.split('\n')[0]}`);
    if (++crashes > 20) throw e;
    await start(); // a crashed tab: load again and carry on from this frame
  }
}
await browser.close(); server.close();
log('capture done');
