// Headless screenshots of the local viewer: node scripts/web/shoot.mjs [url]
// needs: cd web/campus && python3 -m http.server 8765 ; playwright from web/tools/node_modules
import { createRequire } from 'module';
const require = createRequire('/workspace/nj-scenes/web/tools/package.json');
const { chromium } = require('playwright');
const url = process.argv[2] || 'http://127.0.0.1:8765/index.html?capture';
const out = '/workspace/nj-scenes/web/screens/';
const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } }); page.setDefaultTimeout(900000);
const logs = []; page.on('console', m => logs.push(m.type() + ': ' + m.text())); page.on('pageerror', e => logs.push('pageerror: ' + e.message));
const failed = []; page.on('requestfailed', r => failed.push(r.url())); page.on('response', r => { if (r.status() >= 400) failed.push(r.status() + ' ' + r.url()); });
const t0 = Date.now();
await page.goto(url);
await page.waitForFunction(() => window.__campus && window.__campus.loaded, null, { timeout: 600000, polling: 1000 });
const load = await page.evaluate(() => window.__campusLoad);
console.log('loaded in', (Date.now() - t0) / 1000, 's', JSON.stringify(load));
const wait = ms => page.waitForTimeout(ms); const tS = () => console.log('t', (Date.now() - t0) / 1000);
await wait(4000); await page.screenshot({ path: out + 'overview.png' }); tS();
await page.evaluate(() => window.__campus.topView()); await wait(4000); await page.screenshot({ path: out + 'top.png' }); tS();
// eye level W of Susan A. Cole Hall (Blender x -200, y -88 -> three x -200, z 88), looking E at the hall
const g = await page.evaluate(() => window.__campus.groundAt(-200, 88));
console.log('ground at Cole W', g);
await page.evaluate(gy => window.__campus.goto(-203, gy + 1.65, 92, -150, gy + 6, 95), g ?? 128);
await wait(4000); await page.screenshot({ path: out + 'eye_cole_hall.png' }); tS();
// eye level on College Ave by the accessible lot (Blender -278,-50.5 looking E)
const g2 = await page.evaluate(() => window.__campus.groundAt(-278, 50.5));
await page.evaluate(gy => window.__campus.goto(-278, gy + 1.65, 50.5, -238, gy + 0.8, 60), g2 ?? 124);
await wait(4000); await page.screenshot({ path: out + 'eye_college_ave.png' }); tS();
// black-frame check
const stats = await page.evaluate(() => { const c = document.getElementById('canvas'); const gl = c.getContext('webgl2'); const w = 64, h = 64; const px = new Uint8Array(w * h * 4);
  gl.readPixels((c.width - w) >> 1, (c.height - h) >> 1, w, h, gl.RGBA, gl.UNSIGNED_BYTE, px); let s = 0; for (let i = 0; i < px.length; i += 4) s += px[i] + px[i + 1] + px[i + 2]; return s / (w * h * 3); });
console.log('centre mean', stats, 'perf', await page.evaluate(() => document.getElementById('performance').textContent));
console.log('failed requests', JSON.stringify(failed)); console.log(logs.filter(l => !l.startsWith('log')).slice(0, 20).join('\n'));
await browser.close();
