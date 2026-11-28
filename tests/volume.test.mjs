import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pattern, region, cutVolume } from '../tools/web-export/volume.mjs';

const SQ = [[0, 0], [10, 0], [10, 10], [0, 10]];
// a U: the square without a notch on its north side (x 4..6, y 5..10)
const U = [[0, 0], [10, 0], [10, 10], [6, 10], [6, 5], [4, 5], [4, 10], [0, 10]];

const pts = list => ({ X: list.map(p => p[0]), Y: list.map(p => p[1]), Z: list.map(p => p[2]) });
const area = (P, keep) => {
  let s = 0;
  for (let t = 0; t < keep.length; t += 3) {
    const [a, b, c] = [keep[t], keep[t + 1], keep[t + 2]];
    const u = [P.X[b] - P.X[a], P.Y[b] - P.Y[a], P.Z[b] - P.Z[a]], v = [P.X[c] - P.X[a], P.Y[c] - P.Y[a], P.Z[c] - P.Z[a]];
    s += Math.hypot(u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]) / 2;
  }
  return s;
};
const near = (a, b, tol = 1e-6) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);
const used = (P, keep) => [...new Set(keep)].map(i => [P.X[i], P.Y[i], P.Z[i]]);

test('a pattern of the plan files may ask for any case with a leading (?i)', () => {
  assert.ok(pattern('(?i)lawn|walk').test('Lawn_grass'));
  assert.ok(!pattern('lawn').test('Lawn_grass'));
});

test('a triangle inside goes, one outside stays as it was', () => {
  const P = pts([[1, 1, 0], [3, 1, 0], [1, 3, 0], [20, 1, 0], [22, 1, 0], [20, 3, 0]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2, 3, 4, 5], region(SQ));
  assert.deepEqual(r.keep, [3, 4, 5]);
  assert.equal(r.removed, 1);
  assert.equal(added.length, 0);
});

test('a wall that runs on past the ring is cut clean on it', () => {
  // a vertical wall along y = 5 from x 5 to 15, z 0..4: two triangles, the ring's east side at x 10
  const P = pts([[5, 5, 0], [15, 5, 0], [15, 5, 4], [5, 5, 4]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2, 0, 2, 3], region(SQ));
  near(area(P, r.keep), 5 * 4, 1e-3);
  for (const [x] of used(P, r.keep)) assert.ok(x >= 10 - 1e-3, `corner at x ${x} inside the ring`);
  // three new corners (bottom, top, and one on the diagonal the two triangles share): no crack
  assert.equal(added.length, 3);
});

test('with a level only what lies above it goes, cut at the level', () => {
  const P = pts([[2, 5, 0], [8, 5, 0], [8, 5, 10], [2, 5, 10]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2, 0, 2, 3], region(SQ), 4);
  near(area(P, r.keep), 6 * 4, 1e-6);
  for (const [, , z] of used(P, r.keep)) assert.ok(z <= 4 + 1e-9);
});

test('above the level and past the ring: the part outside the ring stays above the level too', () => {
  const P = pts([[5, 5, 0], [15, 5, 0], [15, 5, 10], [5, 5, 10]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2, 0, 2, 3], region(SQ), 4);
  // kept: the whole 10 x 4 strip below the level and the 5 x 6 part above it east of the ring
  near(area(P, r.keep), 10 * 4 + 5 * 6, 1e-3);
});

test('a triangle that lies wholly below the level stays whole', () => {
  const P = pts([[2, 2, 0], [4, 2, 0], [2, 4, 1]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2], region(SQ), 4);
  assert.deepEqual(r.keep, [0, 1, 2]);
  // above the level but outside the ring: whole too, without pieces
  const Q = pts([[20, 5, 0], [22, 5, 0], [22, 5, 10]]), more = [];
  assert.deepEqual(cutVolume(Q, more, [0, 1, 2], region(SQ), 4).keep, [0, 1, 2]);
});

test('between two levels a door goes through a wall: the wall stays round it', () => {
  // a wall along y = 5 from x -5 to 15, z 0..10; the ring takes x 0..10; the door band z 1..3.4
  const P = pts([[-5, 5, 0], [15, 5, 0], [15, 5, 10], [-5, 5, 10]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2, 0, 2, 3], region(SQ), 1, 3.4);
  near(area(P, r.keep), 20 * 10 - 10 * 2.4, 1e-3);
  // no kept piece lies inside the opening
  for (let t = 0; t < r.keep.length; t += 3) {
    const c = [r.keep[t], r.keep[t + 1], r.keep[t + 2]].map(i => [P.X[i], P.Z[i]]);
    const [x, z] = [(c[0][0] + c[1][0] + c[2][0]) / 3, (c[0][1] + c[1][1] + c[2][1]) / 3];
    assert.ok(!(x > 1e-3 && x < 10 - 1e-3 && z > 1 + 1e-3 && z < 3.4 - 1e-3), `piece at ${x}, ${z} in the door`);
  }
});

test('with only an upper level what lies above it stays', () => {
  const P = pts([[2, 5, 0], [8, 5, 0], [8, 5, 10], [2, 5, 10]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2, 0, 2, 3], region(SQ), null, 4);
  near(area(P, r.keep), 6 * 6, 1e-6);
  for (const [, , z] of used(P, r.keep)) assert.ok(z >= 4 - 1e-9);
  // wholly above it: whole
  const Q = pts([[2, 2, 5], [4, 2, 5], [2, 4, 6]]), more = [];
  assert.deepEqual(cutVolume(Q, more, [0, 1, 2], region(SQ), null, 4).keep, [0, 1, 2]);
});

test('a wall whose ends both lie inside keeps the part in a notch of the ring', () => {
  // a wall along y = 8 from x 1 to 9: both ends inside the U, the middle (x 4..6) in the notch
  const P = pts([[1, 8, 0], [9, 8, 0], [9, 8, 3], [1, 8, 3]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2, 0, 2, 3], region(U));
  near(area(P, r.keep), 2 * 3, 0.02);
  for (const [x] of used(P, r.keep)) assert.ok(x >= 4 - 0.01 && x <= 6 + 0.01, `x ${x}`);
});

test('a ground triangle round a ring corner keeps its part outside', () => {
  const P = pts([[8, 8, 1], [14, 8, 1], [8, 14, 1]]), added = [];
  const r = cutVolume(P, added, [0, 1, 2], region(SQ));
  near(area(P, r.keep), 18 - 4, 1e-3); // the triangle less the 2 x 2 corner of the square in it
});
