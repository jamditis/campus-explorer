// Shared helpers for the headless viewer checks: a static file server for the checkout and a
// Chromium launch that renders WebGL in software, so the checks run on a machine with no GPU.
import { createServer } from 'node:http';
import { createReadStream, statSync } from 'node:fs';
import { createRequire } from 'node:module';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = resolve(fileURLToPath(new URL('../..', import.meta.url)));
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json', '.glb': 'model/gltf-binary', '.webp': 'image/webp',
  '.png': 'image/png', '.svg': 'image/svg+xml',
};

/** Serve `root` on a free local port. Resolves { url, close }. */
export function serve(root = ROOT) {
  const server = createServer((req, res) => {
    const path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
    let file = join(root, path);
    try {
      if (statSync(file).isDirectory()) file = join(file, 'index.html');
      const { size } = statSync(file);
      res.writeHead(200, { 'content-type': TYPES[extname(file)] ?? 'application/octet-stream', 'content-length': size, 'cache-control': 'no-store' });
      createReadStream(file).pipe(res);
    } catch { res.writeHead(404).end('not found'); }
  });
  return new Promise(done => server.listen(0, '127.0.0.1', () => done({ url: `http://127.0.0.1:${server.address().port}/`, close: () => server.close() })));
}

/** Playwright from this project's environment: a normal install, or the folder named by PLAYWRIGHT_PATH. */
async function playwright() {
  try { return await import('playwright'); } catch { /* not installed next to the repo */ }
  const require = createRequire(join(process.env.PLAYWRIGHT_PATH ?? '/opt/node-tools/node_modules', 'x.js'));
  return require('playwright');
}

/** Open the viewer in headless Chromium. Collects console errors, page errors and failed requests in `problems`. */
export async function open(url, { width = 1280, height = 800, touch = false, init = null } = {}) {
  const { chromium } = await playwright();
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] });
  const context = await browser.newContext({ viewport: { width, height }, hasTouch: touch });
  const page = await context.newPage(); page.setDefaultTimeout(30 * 60 * 1000);
  const problems = [];
  page.on('console', m => { if (m.type() === 'error') problems.push(`console: ${m.text()}`); });
  page.on('pageerror', e => problems.push(`page error: ${e.message}`));
  page.on('requestfailed', r => { if (r.failure()?.errorText !== 'net::ERR_ABORTED') problems.push(`request failed: ${r.url()}`); });
  page.on('response', r => { if (r.status() >= 400) problems.push(`HTTP ${r.status()}: ${r.url()}`); });
  if (init) await page.addInitScript(init);
  await page.goto(url);
  return { browser, page, problems };
}

/** Wait until the first tiles are in (`ready`) or every tile is in (`loaded`). */
export const waitFor = (page, flag) => page.waitForFunction(f => window.__campus?.[f], flag, { polling: 500 });
