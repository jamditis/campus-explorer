import test from 'node:test';
import assert from 'node:assert/strict';
import { flightLimit, limitVelocity, clampToLimit, MARGIN, SKIRT_INSET, SOFT, CEILING_SPAN } from '../viewer/flight-math.js';

// tiles on a 160 m grid: centres from x -560..400 and z -1360..400, as in models/main today
const TILES = [{ center: [-560, -1360] }, { center: [400, 400] }, { center: [0, 0] }, { file: 'skirt.glb' }];
const L = flightLimit(TILES, { skirtHalf: 2000, floorY: 100 });

test('the limit is the campus tile box grown by the margin, inside the far-field skirt', () => {
  assert.equal(MARGIN, 1000);
  assert.equal(L.x0, -640 - 1000);
  assert.equal(L.x1, 480 + 1000);
  assert.equal(L.z1, 480 + 1000);
  assert.equal(L.z0, -(2000 - SKIRT_INSET)); // grown to -2440, cut back inside the skirt
  // the ceiling is above the top view (span x 1.05 over the floor)
  const span = 1920;
  assert.equal(L.y1, 100 + span * CEILING_SPAN);
  assert.ok(L.y1 > 100 + span * 1.05);
  assert.equal(flightLimit([], {}), null);
});

test('inside and away from the limit the velocity is unchanged', () => {
  assert.deepEqual(limitVelocity({ x: 0, y: 200, z: 0 }, { x: 300, y: 0, z: -40 }, L), { x: 300, y: 0, z: -40 });
});

test('near the limit the outward part slows and the inward part does not', () => {
  const p = { x: L.x1 - SOFT / 2, y: 200, z: 0 };
  const out = limitVelocity(p, { x: 100, y: 0, z: 30 }, L);
  assert.ok(Math.abs(out.x - 50) < 1e-9); // half way into the soft band: half speed outward
  assert.equal(out.z, 30); // sliding along the edge is free
  assert.deepEqual(limitVelocity(p, { x: -100, y: 0, z: 30 }, L), { x: -100, y: 0, z: 30 }); // back toward the campus
  assert.equal(limitVelocity({ x: L.x1, y: 200, z: 0 }, { x: 100, y: 0, z: 0 }, L).x, 0);
  assert.equal(limitVelocity({ x: 0, y: L.y1 - 1, z: 0 }, { x: 0, y: 100, z: 0 }, L).y, 100 / SOFT);
});

test('outside the limit a position is clamped; inside it is unchanged', () => {
  assert.deepEqual(clampToLimit({ x: 9000, y: 9000, z: -9000 }, L), { x: L.x1, y: L.y1, z: L.z0 });
  assert.deepEqual(clampToLimit({ x: 1, y: 2, z: 3 }, L), { x: 1, y: 2, z: 3 });
  assert.deepEqual(clampToLimit({ x: 1, y: 2, z: 3 }, null), { x: 1, y: 2, z: 3 });
});

test('holding forward toward the limit ends at it without crossing or bouncing back', () => {
  const p = { x: 0, y: 200, z: 0 }; let last = -Infinity;
  for (let i = 0; i < 4000; i++) {
    const v = limitVelocity(p, { x: 1200, y: 0, z: 0 }, L); // the fastest fly speed (400 m/s, run x 3)
    p.x += v.x * 0.1; // a slow frame
    Object.assign(p, clampToLimit(p, L));
    assert.ok(p.x >= last - 1e-9 && p.x <= L.x1); last = p.x;
  }
  assert.ok(L.x1 - p.x < 0.5);
});
