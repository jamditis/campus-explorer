import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { CANOPY, canopyUv, crownShare, crownNoise, NOISE_Q } from '../viewer/farview-math.js';

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

test('the noise quantiles match the noise, and crowns over it cover the map\'s share near and far', () => {
  const v = [];
  for (let x = 3000; x < 9000; x += 7.3) for (let z = -4000; z < 2000; z += 7.9) v.push(crownNoise(x, z));
  const sorted = [...v].sort((a, b) => a - b);
  for (let k = 1; k < 20; k++) assert.ok(Math.abs(sorted[Math.round((k / 20) * (sorted.length - 1))] - NOISE_Q[k]) < 0.01, `quantile ${k * 5} %`);
  for (const cover of [0.05, 0.2, 0.5, 0.8, 0.95]) {
    const near = v.reduce((s, n) => s + crownShare(cover, n, 1), 0) / v.length;
    assert.ok(Math.abs(near - cover) < 0.02, `cover ${cover}: crowns ${near.toFixed(3)}`);
    assert.equal(crownShare(cover, 0.3, 0), cover, 'far: the share itself');
  }
});
