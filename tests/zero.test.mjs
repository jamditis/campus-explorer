import { test } from 'node:test';
import assert from 'node:assert/strict';
import { zeroArea, keepTriangles } from '../tools/web-export/zero.mjs';

// a unit square (two triangles) and, on top of it, slivers that draw nothing
const P = Int16Array.from([0, 0, 0, 10, 0, 0, 10, 10, 0, 0, 10, 0, 5, 0, 0, 0, 0, 0]);
// vertex 4 lies on the edge 0-1; vertex 5 is a second copy of vertex 0

test('a triangle with two equal corners, or with three corners on one line, has zero area', () => {
  assert.equal(zeroArea(P, 0, 1, 2), false);
  assert.equal(zeroArea(P, 0, 0, 2), true); // same index twice
  assert.equal(zeroArea(P, 0, 5, 2), true); // same position under two indices
  assert.equal(zeroArea(P, 0, 4, 1), true); // collinear
  assert.equal(zeroArea(P, 4, 2, 3), false);
});

test('keepTriangles drops only zero-area triangles and keeps the order of the rest', () => {
  const I = Uint16Array.from([0, 1, 2, 0, 5, 2, 0, 2, 3, 0, 4, 1, 1, 1, 1]);
  const out = keepTriangles(I, P);
  assert.deepEqual([...out], [0, 1, 2, 0, 2, 3]);
  assert.equal(out.constructor, Uint16Array);
  assert.equal(keepTriangles(Uint32Array.from([0, 1, 2]), P), null); // nothing to drop: null, no copy
});

test('float positions too, compared exactly', () => {
  const F = Float32Array.from([0, 0, 0, 1e-3, 0, 0, 0, 1e-3, 0, 1e-3, 0, 0]);
  assert.equal(zeroArea(F, 0, 1, 2), false); // tiny but real
  assert.equal(zeroArea(F, 0, 1, 3), true);
});
