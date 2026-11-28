import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { CANOPY, canopyUv, crownShare } from '../viewer/farview-math.js';

test('the canopy box is canopy.json\'s Blender box in the viewer frame', () => {
  const meta = JSON.parse(readFileSync(new URL('../viewer/canopy.json', import.meta.url)));
  const [x0, y0, x1, y1] = meta.box; // Blender x east, y north; rows run north to south
  assert.deepEqual(CANOPY.box, [x0, -y1, x1, -y0]);
  assert.deepEqual(meta.size, [(x1 - x0) / meta.cell, (y1 - y0) / meta.cell]);
});

test('map coordinates: row 0 is the north edge, outside is null', () => {
  assert.deepEqual(canopyUv(-10000, -10000), [0, 0]);
  assert.deepEqual(canopyUv(21980, 20000), [1, 1]);
  assert.equal(canopyUv(-10001, 0), null);
  const [u, v] = canopyUv(0, 0); // the campus origin
  assert.ok(Math.abs(u - 10000 / 31980) < 1e-12 && Math.abs(v - 10000 / 30000) < 1e-12);
});

test('crowns cover the share the map gives, near and far', () => {
  for (const cover of [0, 0.2, 0.5, 0.8, 1]) {
    let sum = 0; const N = 2000;
    for (let i = 0; i < N; i++) sum += crownShare(cover, (i + 0.5) / N, 1); // evenly spread noise
    assert.ok(Math.abs(sum / N - cover) < 0.01, `near ${cover}: ${sum / N}`);
    assert.equal(crownShare(cover, 0.3, 0), cover, 'far: the share itself');
  }
});
