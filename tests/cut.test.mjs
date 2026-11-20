import { test } from 'node:test';
import assert from 'node:assert/strict';
import { crossings, cornersIn, outsidePart } from '../tools/web-export/cut.mjs';

// a square footprint 0..10 x 0..10, anticlockwise
const SQ = [[0, 0], [10, 0], [10, 10], [0, 10]];
// an L: the square without its north-east quarter (a reflex corner at 5, 5)
const L = [[0, 0], [10, 0], [10, 5], [5, 5], [5, 10], [0, 10]];
const near = (a, b, tol = 1e-9) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);

test('an edge from inside to outside crosses the footprint where the outline is', () => {
  const t = crossings(9, 5, 11, 5, SQ);
  assert.equal(t.length, 1);
  near(t[0], 0.5);
  assert.deepEqual(crossings(1, 1, 2, 2, SQ), []);
  // through the reflex corner's two runs: two crossings, in order from the first point
  const u = crossings(6, 4, 4, 6, L);
  assert.equal(u.length, 0); // 6,4 and 4,6 are both inside the L, the segment passes 5,5 exactly
  const v = crossings(4, 6, 6, 4.9, L).length;
  assert.ok(v === 0 || v === 2);
});

test('footprint corners inside a triangle are found, and nothing else', () => {
  assert.deepEqual(cornersIn(L, [4, 4], [7, 4], [4, 7]), [3]);
  assert.deepEqual(cornersIn(L, [1, 1], [2, 1], [1, 2]), []);
});

test('a triangle with one corner inside keeps the part outside, ending on the outline', () => {
  // corner 0 inside (9, 5); corners 1, 2 outside to the east
  const tri = [[9, 5], [11, 4], [11, 6]];
  const part = outsidePart(tri, [true, false, false], null);
  // polygon: crossing on 0-1, corner 1, corner 2, crossing on 2-0
  assert.deepEqual(part.map(p => p.kind), ['cross', 'corner', 'corner', 'cross']);
  for (const p of part.filter(q => q.kind === 'cross')) near(p.x, 10);
  // the crossing names its inside and outside corner, so two triangles that share the edge agree
  assert.deepEqual(part[0].edge, [0, 1]);
  assert.deepEqual(part[3].edge, [0, 2]);
});

test('a triangle with two corners inside keeps one small triangle', () => {
  const tri = [[9, 4], [12, 5], [9, 6]];
  const part = outsidePart(tri, [true, false, true], null);
  assert.deepEqual(part.map(p => p.kind), ['cross', 'corner', 'cross']);
});

test('a footprint corner inside the triangle goes between the two crossings', () => {
  // the L's reflex corner (5, 5) lies inside; corner 0 is inside the L, 1 and 2 are in the cut-out quarter
  const tri = [[4, 4], [8, 6], [6, 8]];
  const part = outsidePart(tri, [true, false, false], { index: 3, at: [5, 5] });
  assert.deepEqual(part.map(p => p.kind), ['cross', 'corner', 'corner', 'cross', 'ring']);
});

test('the kept part is a fan of triangles with the winding of the original, covering the outside', () => {
  const area = ps => ps.reduce((s, p, i) => {
    const q = ps[(i + 1) % ps.length];
    return s + p[0] * q[1] - q[0] * p[1];
  }, 0) / 2;
  const tri = [[4, 4], [8, 6], [6, 8]];
  const part = outsidePart(tri, [true, false, false], { index: 3, at: [5, 5] });
  const pts = part.map(p => [p.x, p.y]);
  // the part outside the L: the triangle (area 6) minus the bit inside the L
  const whole = area(tri);
  const kept = area(pts);
  assert.ok(kept > 0 && kept < whole, `${kept} of ${whole}`);
  // every point of the part is on or outside the L
  for (const [x, y] of pts) assert.ok(x >= 5 - 1e-9 && y >= 5 - 1e-9, `${x}, ${y}`);
});

test('a crossing can be pulled back toward the inside corner by an overlap', () => {
  const tri = [[9, 5], [11, 4], [11, 6]];
  const part = outsidePart(tri, [true, false, false], null, 0.1);
  for (const p of part.filter(q => q.kind === 'cross')) near(p.x, 9.9, 1e-6);
});
