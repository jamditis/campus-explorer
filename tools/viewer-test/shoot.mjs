// The standard views for before/after comparison. Same camera poses every time.
//   node tools/viewer-test/shoot.mjs <outdir> [--url URL] [--quality low|medium|high] [--slow-load]
// Without --url it serves this checkout. --slow-load is for viewers that draw every frame while
// loading (versions before draw-on-demand): it spaces their frames out so software rendering can finish.
import { mkdirSync } from 'node:fs';
import { open, serve, waitFor } from './lib.mjs';

const args = process.argv.slice(2), flag = n => { const i = args.indexOf(n); return i < 0 ? null : args.splice(i, 2)[1]; };
const slow = args.includes('--slow-load'); if (slow) args.splice(args.indexOf('--slow-load'), 1);
const given = flag('--url'), quality = flag('--quality') ?? 'medium', out = args[0];
if (!out) { console.error('usage: node tools/viewer-test/shoot.mjs <outdir> [--url URL] [--quality q] [--slow-load]'); process.exit(2); }
mkdirSync(out, { recursive: true });

// [name, camera x, y, z, target x, y, z]; y of null means "ground height at ground[x, z] plus the offset"
const VIEWS = [
  { name: 'overview', pose: [181.9, 350.75, 410.6, -45, 120, 60] },
  { name: 'top', pose: [-45, 882.5, 60.01, -45, 95, 60] },
  { name: 'eye_cole_hall', ground: [-200, 88], pose: [-203, 1.65, 92, -150, 6, 95] },      // eye level west of Susan A. Cole Hall, looking east
  { name: 'eye_college_ave', ground: [-278, 50.5], pose: [-278, 1.65, 50.5, -238, 0.8, 60] }, // College Avenue by the accessible lot
  { name: 'lot_oblique', ground: [-235, 75], pose: [-232, 28, 112, -236, 0, 74] },          // painted markings in the accessible lot
  { name: 'north_oblique', pose: [60, 420, -330, -150, 115, -760] },                         // north campus toward the station
  { name: 'seam_oblique', pose: [-420, 330, -40, -150, 130, -260] },                         // where the two source models meet
  { name: 'sw_top', ground: [-400, 215], pose: [-400, 330, 215.01, -400, 0, 215] },          // southwest corner: station, Normal Avenue, Sprague Field
  { name: 'sw_station', ground: [-454, 266], pose: [-395, 45, 300, -456, 0, 262] },          // Montclair Heights station and its lot, from the east
  { name: 'sw_field', ground: [-336, 157], pose: [-430, 80, 250, -336, 0, 157] },            // Sprague Field from the south-west
  { name: 'eye_crossing', ground: [-415, 232], pose: [-415, 1.7, 232.5, -447, 2.2, 224.5] }, // Normal Avenue grade crossing at eye level
  { name: 'tv_oblique', ground: [-280, -520], pose: [-385, 95, -415, -275, 0, -535] },       // TV Tower block and the Clove Road junction from the south-west
  { name: 'tv_mast', ground: [-247, -544], pose: [-470, 45, -330, -247, 95, -544] },        // the TV Tower mast, whole height, from the south-west
  { name: 'eye_clove_yb', ground: [-299.5, -492], pose: [-299.5, 1.65, -492, -262, 6, -552] }, // Clove Road / Yogi Berra Drive junction at eye level, looking north-east
  { name: 'eye_rec_center', ground: [165, -560], pose: [165, 1.65, -560, 205, 12, -605] },    // Student Recreation Center's south-west pavilion at eye level
];

const server = given ? null : await serve();
const url = `${given ?? server.url}?capture&quality=${quality}`;
const init = slow ? () => {
  const raf = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = fn => (window.__campus?.loaded ? raf(fn) : setTimeout(() => raf(fn), 4000));
} : null;
const { browser, page, problems } = await open(url, { init, minutes: slow ? 180 : 45 });
const t0 = Date.now(), secs = () => ((Date.now() - t0) / 1000).toFixed(0);
await waitFor(page, 'loaded');
console.log(`loaded in ${secs()} s`);
await page.addStyleTag({ content: 'body>:not(#viewer){display:none!important}' });
for (const v of VIEWS) {
  const pose = await page.evaluate(({ ground, pose }) => {
    const p = [...pose];
    if (ground) { const g = window.__campus.groundAt(...ground) ?? 125; p[1] += g; p[4] += g; }
    window.__campus.goto(...p); return p;
  }, v);
  await page.waitForTimeout(slow ? 12000 : 5000);
  await page.screenshot({ path: `${out}/${v.name}.png` });
  console.log(`${v.name} at ${secs()} s`, pose.map(n => +n.toFixed(1)).join(' '));
}
if (problems.length) console.log(`problems:\n${problems.join('\n')}`);
await browser.close(); server?.close();
process.exit(problems.length ? 1 : 0);
