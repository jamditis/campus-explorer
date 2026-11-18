// Headless smoke test of the viewer: loads a few tiles, exercises every mode and tool, and fails on
// any console error, page error or failed request.
//   node tools/viewer-test/smoke.mjs [--tiles N] [--url URL]
import assert from 'node:assert/strict';
import { open, serve, waitFor } from './lib.mjs';

const args = process.argv.slice(2), flag = (n, d) => { const i = args.indexOf(n); return i < 0 ? d : args[i + 1]; };
const server = flag('--url') ? null : await serve();
const base = flag('--url') ?? server.url;
const { browser, page, problems } = await open(`${base}?tiles=${flag('--tiles', 3)}&quality=low`);
const step = async (name, fn) => { const t = Date.now(); await fn(); console.log(`ok   ${name} (${((Date.now() - t) / 1000).toFixed(1)} s)`); };
const app = fn => page.evaluate(fn);
const settle = (ms = 600) => page.waitForTimeout(ms);
let failed = false;
try {
  await step('first tiles arrive and the view is usable', async () => {
    await waitFor(page, 'ready');
    assert.equal(await page.isHidden('#load'), true);
  });
  await step('tools start', async () => {
    await page.waitForFunction(() => document.querySelector('.hud-compass, [class^="hud-"]') && document.querySelector('#tool-labels[aria-pressed]'));
    for (const id of ['tool-labels', 'tool-map', 'tool-measure', 'tool-tour', 'tool-hunt']) assert.equal(await page.isDisabled(`#${id}`), false, `${id} is disabled: its module failed to start`);
  });
  await step('every tile loads', () => waitFor(page, 'loaded'));
  await step('sunlight follows the real sun', async () => {
    const day = await app(() => window.__campus.app.sun);
    assert.ok(day.elevation > 30 && day.azimuth > 180 && day.azimuth < 260, `default light should be an afternoon sun in the south-west: ${JSON.stringify(day)}`);
    await page.fill('#sun-date', '2026-12-21'); await page.dispatchEvent('#sun-date', 'change');
    await app(() => { const s = document.getElementById('sun-time'); s.value = 12 * 60; s.dispatchEvent(new Event('input')); });
    const noon = await app(() => window.__campus.app.sun);
    assert.ok(Math.abs(noon.elevation - 25.7) < 1, `winter solstice noon elevation ${noon.elevation}`);
    await app(() => { const s = document.getElementById('sun-time'); s.value = 23 * 60; s.dispatchEvent(new Event('input')); });
    assert.ok((await app(() => window.__campus.app.look.night)) > 0.9, 'night');
    await page.click('#sun-reset');
  });
  await step('search flies to a place', async () => {
    await page.fill('#search', 'kasser');
    await page.waitForSelector('#search-results li');
    await page.keyboard.press('Enter');
    await page.waitForFunction(() => { const t = window.__campus.controls.target; return Math.hypot(t.x + 216, t.z - 30) < 15; });
  });
  await step('walk mode stands on the ground and moves', async () => {
    await app(() => window.__campus.app.setMode('walk', { at: new window.__campus.THREE.Vector3(-203, 200, 92) }));
    const a = await app(() => window.__campus.app.player.position.toArray());
    assert.ok(a[1] > 100 && a[1] < 170, `feet at ${a[1]}`);
    await page.keyboard.down('KeyW'); await settle(2500); await page.keyboard.up('KeyW');
    const b = await app(() => window.__campus.app.player.position.toArray());
    assert.ok(Math.hypot(b[0] - a[0], b[2] - a[2]) > 0.5, 'the player did not move');
    assert.ok(Math.abs(b[1] - a[1]) < 6, 'the player left the ground');
    await page.keyboard.press('KeyV');
    assert.equal(await app(() => window.__campus.app.state.view), 'third');
  });
  await step('fly mode moves the camera', async () => {
    await page.keyboard.press('Digit2');
    const a = await app(() => window.__campus.camera.position.toArray());
    await page.keyboard.down('KeyW'); await settle(1500); await page.keyboard.up('KeyW');
    const b = await app(() => window.__campus.camera.position.toArray());
    assert.ok(Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) > 2, 'the camera did not move');
    await page.keyboard.press('Digit1');
    assert.equal(await app(() => window.__campus.app.state.mode), 'orbit');
  });
  await step('tools toggle', async () => {
    for (const [key, id] of [['KeyL', 'tool-labels'], ['KeyM', 'tool-map'], ['KeyR', 'tool-measure'], ['KeyH', 'tool-hunt']]) {
      const before = await page.getAttribute(`#${id}`, 'aria-pressed');
      await page.keyboard.press(key); await settle(300);
      assert.notEqual(await page.getAttribute(`#${id}`, 'aria-pressed'), before, `${id} did not toggle`);
      await page.keyboard.press(key); await settle(300);
    }
  });
  await step('the share link restores the view', async () => {
    await app(() => window.__campus.goto(-120, 260, 140, -180, 130, 60));
    await settle(1500);
    const hash = await app(() => location.hash);
    assert.match(hash, /c=-120\.0,260\.0,140\.0/);
    await app(() => window.__campus.goto(0, 500, 0, 0, 120, -1));
    await app(h => { location.hash = '#x'; location.hash = h; }, hash);
    await page.waitForFunction(() => Math.abs(window.__campus.camera.position.x + 120) < 0.2);
  });
  await step('nothing is drawn while the view is still', async () => {
    await settle(2500);
    const n = await app(() => new Promise(done => { let c = 0; const off = window.__campus.app.on('drawn', () => c++); setTimeout(() => { off(); done(c); }, 1500); }));
    assert.ok(n <= 2, `${n} frames drawn while idle`);
  });
  await step('phone size', async () => {
    await page.setViewportSize({ width: 390, height: 844 }); await settle(800);
    assert.equal(await page.isVisible('#panel-toggle'), true);
  });
  assert.deepEqual(problems, [], 'the page reported problems');
} catch (e) {
  failed = true; console.error(`FAIL ${e.message}`);
  if (problems.length) console.error(problems.join('\n'));
}
await browser.close(); server?.close();
process.exit(failed ? 1 : 0);
