// Headless smoke test of the viewer: loads a few tiles, exercises every mode and tool, and fails on
// any console error, page error or failed request.
//   node tools/viewer-test/smoke.mjs [--tiles N] [--url URL]
import assert from 'node:assert/strict';
import { open, serve, waitFor } from './lib.mjs';

const args = process.argv.slice(2), flag = (n, d) => { const i = args.indexOf(n); return i < 0 ? d : args[i + 1]; };
const server = flag('--url') ? null : await serve();
const base = flag('--url') ?? server.url;
// --tiles keeps the N tiles nearest the view. The link aims the view at the heart of the campus
// (Kasser Theater, Cole Hall), where the steps below search, walk and measure.
const START = '#v=1&m=orbit&c=-120.0,260.0,140.0&t=-200.0,130.0,80.0';
const { browser, page, problems } = await open(`${base}?tiles=${flag('--tiles', 3)}&quality=low${START}`);
const step = async (name, fn) => { const t = Date.now(); await fn(); console.log(`ok   ${name} (${((Date.now() - t) / 1000).toFixed(1)} s)`); };
const app = fn => page.evaluate(fn);
const settle = (ms = 600) => page.waitForTimeout(ms);
const MOVE_MS = 180000; // longest wait for a held key to move the view
let failed = false;
try {
  await step('first tiles arrive and the view is usable', async () => {
    await waitFor(page, 'ready');
    assert.equal(await page.isHidden('#load'), true);
  });
  await step('tools start', async () => {
    await page.waitForSelector('.hud-compass');
    for (const id of ['tool-labels', 'tool-map', 'tool-measure', 'tool-tour', 'tool-hunt']) assert.equal(await page.isDisabled(`#${id}`), false, `${id} is disabled: its module failed to start`);
    // the overlay ignores pointer events; a control inside it must still take a click
    assert.match(await app(() => { const b = document.querySelector('.hud-compass').getBoundingClientRect(); return document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2)?.closest('button')?.className ?? 'nothing'; }), /hud-compass/);
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
    // hold the key until the player has moved: software rendering can take seconds per frame
    await page.keyboard.down('KeyW');
    await page.waitForFunction(([x, z]) => { const p = window.__campus.app.player.position; return Math.hypot(p.x - x, p.z - z) > 0.5; }, [a[0], a[2]], { timeout: MOVE_MS })
      .catch(() => assert.fail('the player did not move')).finally(() => page.keyboard.up('KeyW'));
    const b = await app(() => window.__campus.app.player.position.toArray());
    assert.ok(Math.abs(b[1] - a[1]) < 6, 'the player left the ground');
    await page.keyboard.press('KeyV');
    assert.equal(await app(() => window.__campus.app.state.view), 'third');
  });
  await step('fly mode moves the camera', async () => {
    await page.keyboard.press('Digit2');
    const a = await app(() => window.__campus.camera.position.toArray());
    await page.keyboard.down('KeyW');
    await page.waitForFunction(([x, y, z]) => { const p = window.__campus.camera.position; return Math.hypot(p.x - x, p.y - y, p.z - z) > 2; }, a, { timeout: MOVE_MS })
      .catch(() => assert.fail('the camera did not move')).finally(() => page.keyboard.up('KeyW'));
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
  await step('cancelling a walk leaves the camera where it was', async () => {
    await app(() => window.__campus.goto(-120, 260, 140, -180, 130, 60));
    const before = await app(() => window.__campus.camera.position.toArray());
    await app(() => { const a = window.__campus.app; a.setMode('walk'); a.setMode('orbit'); });
    await settle(2500);
    const after = await app(() => window.__campus.camera.position.toArray());
    assert.ok(Math.hypot(after[0] - before[0], after[1] - before[1], after[2] - before[2]) < 0.01, `camera moved from ${before} to ${after}`);
  });
  await step('a share link applies from fly mode too', async () => {
    await page.keyboard.press('Digit2');
    await app(() => { location.hash = '#v=1&m=orbit&c=10.0,300.0,200.0&t=-50.0,130.0,0.0'; });
    await page.waitForFunction(() => window.__campus.app.state.mode === 'orbit' && Math.abs(window.__campus.camera.position.x - 10) < 0.2);
  });
  await step('the share link restores the view', async () => {
    await app(() => window.__campus.goto(-120, 260, 140, -180, 130, 60));
    // the link is written a moment after the view stops changing
    await page.waitForFunction(() => /c=-120\.0,260\.0,140\.0/.test(location.hash), null, { timeout: MOVE_MS }).catch(() => assert.fail('the address bar did not get the view'));
    const hash = await app(() => location.hash);
    await app(() => window.__campus.goto(0, 500, 0, 0, 120, -1));
    await app(h => { location.hash = '#x'; location.hash = h; }, hash);
    await page.waitForFunction(() => Math.abs(window.__campus.camera.position.x + 120) < 0.2);
  });
  await step('nothing is drawn while the view is still', async () => {
    // the last frames after a move (sharpening, late textures) can take a while in software; then it must go quiet
    let n = Infinity;
    for (let i = 0; i < 20 && n > 0; i++) n = await app(() => new Promise(done => { let c = 0; const off = window.__campus.app.on('drawn', () => c++); setTimeout(() => { off(); done(c); }, 3000); }));
    assert.equal(n, 0, `${n} frames drawn in 3 s while idle`);
  });
  await step('phone size', async () => {
    await page.setViewportSize({ width: 390, height: 844 }); await settle(800);
    assert.equal(await page.isVisible('#panel-toggle'), true);
  });
  assert.deepEqual(problems, [], 'the page reported problems');
  await step('phone profile: lite mode, touch controls, full screen', async () => {
    const phone = await open(`${base}?lite=1&quality=low`, { width: 390, height: 844, touch: true });
    const p = phone.page;
    try {
      await waitFor(p, 'ready');
      assert.equal(await p.evaluate(() => window.__campus.app.world.budget), 9);
      assert.equal(await p.evaluate(() => document.getElementById('mode-group').parentElement.id), 'mode-slot', 'the mode switch belongs in the top bar on a phone');
      await p.tap('#walk');
      await p.waitForFunction(() => window.__campus.app.state.mode === 'walk' && !window.__campus.app.player.busy);
      await p.touchscreen.tap(300, 420); // the first touch on the view brings up the touch controls
      await p.waitForSelector('.touch-jump', { state: 'visible' });
      assert.match(await p.evaluate(() => { const b = document.querySelector('.touch-jump').getBoundingClientRect(); return document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2)?.className ?? 'nothing'; }), /touch-jump/, 'the jump button does not receive taps');
      await p.tap('#fullscreen');
      await p.waitForFunction(() => document.getElementById('fullscreen').getAttribute('aria-pressed') === 'true');
      // tiles in memory stay within the budget (plus the slack that stops flip-flopping)
      const ready = await p.evaluate(() => window.__campus.app.world.tiles.filter(t => t.center && t.state === 'ready').length);
      assert.ok(ready <= 11, `${ready} centred tiles in memory`);
      assert.deepEqual(phone.problems, [], 'the phone page reported problems');
    } finally { await phone.browser.close(); }
  });
} catch (e) {
  failed = true; console.error(`FAIL ${e.message}`);
  if (problems.length) console.error(problems.join('\n'));
}
await browser.close(); server?.close();
process.exit(failed ? 1 : 0);
