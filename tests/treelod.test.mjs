import test from 'node:test';
import assert from 'node:assert/strict';
import {
  barkOrder, reorderIndex, thinPick, scaleLinear, pixels, treeBand,
  TREE_MID, TREE_FAR_MID, BARK_MIN_DIAMETER, BARK_SHARE, SHRUB_REACH, SHRUB_THIN,
} from '../viewer/treelod-math.js';

// A closed-sided tube along +y: `sides` quads round, radius r, length len, at x0. `split` gives every quad its
// own four vertices (as an exporter does at UV and normal seams), so only welding by position joins them.
function tube(pos, idx, { r, len, x0 = 0, sides = 6, split = false }) {
  const ring = (k, y) => [x0 + r * Math.cos(2 * Math.PI * k / sides), y, r * Math.sin(2 * Math.PI * k / sides)];
  const add = p => { pos.push(...p); return pos.length / 3 - 1; };
  if (!split) {
    const base = pos.length / 3;
    for (let k = 0; k < sides; k++) { add(ring(k, 0)); add(ring(k, len)); }
    for (let k = 0; k < sides; k++) {
      const a = base + 2 * k, b = base + 2 * ((k + 1) % sides);
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
  } else {
    for (let k = 0; k < sides; k++) {
      const a = add(ring(k, 0)), b = add(ring(k + 1, 0)), c = add(ring(k, len)), d = add(ring(k + 1, len));
      idx.push(a, b, c, b, d, c);
    }
  }
}
function mesh(parts) {
  const pos = [], idx = [];
  for (const p of parts) tube(pos, idx, p);
  return { position: new Float32Array(pos), index: Uint16Array.from(idx) };
}

test('bark: thin branches go to the end of the order, thick ones are kept, each triangle once', () => {
  // a 2 cm twig (12 triangles) between two 20 cm limbs
  const m = mesh([{ r: 0.1, len: 2 }, { r: 0.01, len: 1, x0: 3 }, { r: 0.1, len: 2, x0: 6 }]);
  const { order, kept } = barkOrder(m.position, m.index, { minDiameter: 0.06 });
  assert.equal(order.length, 36);
  assert.deepEqual(kept, [24]);
  assert.deepEqual([...order].sort((a, b) => a - b), [...Array(36).keys()]);
  // stable: the kept limbs first in their own order, then the twig
  assert.deepEqual([...order.slice(0, 24)], [...Array(12).keys(), ...Array.from({ length: 12 }, (_, i) => 24 + i)]);
  assert.deepEqual([...order.slice(24)], Array.from({ length: 12 }, (_, i) => 12 + i));
});

test('bark: the diameter is measured in world metres through the scale', () => {
  const m = mesh([{ r: 0.01, len: 0.5 }]); // 2 cm in mesh units
  assert.deepEqual(barkOrder(m.position, m.index, { minDiameter: 0.06 }).kept, [0]);
  assert.deepEqual(barkOrder(m.position, m.index, { minDiameter: 0.06, scale: 5 }).kept, [12]); // 10 cm in the world
});

test('bark: a branch split at its seams still counts as one branch of its true diameter', () => {
  const m = mesh([{ r: 0.1, len: 2, split: true }]);
  assert.deepEqual(barkOrder(m.position, m.index, { minDiameter: 0.06 }).kept, [12]);
  const thin = mesh([{ r: 0.01, len: 2, split: true }]);
  assert.deepEqual(barkOrder(thin.position, thin.index, { minDiameter: 0.06 }).kept, [0]);
});

test('bark: thin pieces are ordered largest first, and each share of area drops the smallest up to it', () => {
  // limb (area 6 x 0.1 x 2 = 1.2), twigs of area 0.12, 0.06 and 0.03 (all 2 cm or less), 12 triangles each
  const m = mesh([{ r: 0.01, len: 0.5, x0: 9 }, { r: 0.1, len: 2 }, { r: 0.01, len: 1, x0: 3 }, { r: 0.01, len: 2, x0: 6 }]);
  const { order, kept } = barkOrder(m.position, m.index, { minDiameter: 0.06, shares: [0, 0.02, 0.05, 0.065, 1] });
  const piece = t => Math.floor(t / 12); // tube k holds triangles 12k .. 12k + 11
  assert.deepEqual([0, 12, 24, 36].map(i => piece(order[i])), [1, 3, 2, 0]); // limb, then twigs by area
  // total area 1.41: 2 % is 0.028 (no twig that small), 5 % is 0.071 (the 0.03 twig), 6.5 % is 0.092 (and the 0.06)
  assert.deepEqual(kept, [48, 48, 36, 24, 12]);
});

test('bark: a mesh without triangles keeps nothing and breaks nothing', () => {
  assert.deepEqual(barkOrder(new Float32Array(0), new Uint16Array(0), { minDiameter: 0.06, shares: [0.1, 1] }), { order: new Uint32Array(0), kept: [0, 0] });
});

test('reorderIndex puts the triangles in the given order, in an array of the same type', () => {
  const index = Uint16Array.from([0, 1, 2, 3, 4, 5, 6, 7, 8]);
  const out = reorderIndex(index, Uint32Array.from([2, 0, 1]));
  assert.ok(out instanceof Uint16Array);
  assert.deepEqual([...out], [6, 7, 8, 0, 1, 2, 3, 4, 5]);
});

test('thinPick keeps about one in k, the same ones every time, in order', () => {
  const a = thinPick(80000, 8), b = thinPick(80000, 8);
  assert.deepEqual(a, b);
  assert.ok(Math.abs(a.length - 10000) < 300, `kept ${a.length}`);
  for (let i = 1; i < a.length; i++) assert.ok(a[i] > a[i - 1]);
  assert.equal(thinPick(0, 8).length, 0);
  assert.equal(thinPick(3, 8).length >= 1, true); // never nothing from a non-empty batch
  assert.equal(thinPick(5, 1).length, 5);
});

test('scaleLinear grows the 3x3 part of a column-major matrix about its own origin', () => {
  const m = Float32Array.from([1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 3, 0, 7, 8, 9, 1, /* second */ 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  scaleLinear(m, 0, 2);
  assert.deepEqual([...m.slice(0, 16)], [2, 0, 0, 0, 0, 4, 0, 0, 0, 0, 6, 0, 7, 8, 9, 1]);
  assert.deepEqual([...m.slice(16)], [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
});

test('treeBand: full near, the two middle versions, the impostor past its distance', () => {
  assert.equal(treeBand(10, 70, 170, 420), 0);
  assert.equal(treeBand(70, 70, 170, 420), 1);
  assert.equal(treeBand(169, 70, 170, 420), 1);
  assert.equal(treeBand(170, 70, 170, 420), 2);
  assert.equal(treeBand(420, 70, 170, 420), 3);
  assert.equal(treeBand(300, 70, 500, 420), 1); // a second middle distance past the impostor's: no second band
  assert.equal(treeBand(450, 70, 500, 420), 3);
});

test('the distances grow with quality and come in order', () => {
  for (const q of ['low', 'medium', 'high']) assert.ok(TREE_MID[q] < TREE_FAR_MID[q], q);
  assert.ok(TREE_FAR_MID.low < TREE_FAR_MID.medium && TREE_FAR_MID.medium < TREE_FAR_MID.high);
  assert.ok(BARK_SHARE.near > 0 && BARK_SHARE.near < BARK_SHARE.far && BARK_SHARE.far <= 1);
});

// The distances are set from what a viewer can see, in CSS pixels of a 1280 x 800 window. The orbit view's 50
// degrees is the narrowest field of view, so the largest pixels-per-metre: there the thickest branch the middle
// version drops is about a pixel wide where it starts at Low, 0.75 px at Medium and half a pixel at High (walk
// view, 68 degrees: 0.71 / 0.51 / 0.36 px). A shrub leaf card (2.1 x 4.6 cm) is under a pixel long and under half
// a pixel wide in the walk view where cards thin out.
test('middle tree and thinned shrub distances keep what they change under a pixel', () => {
  const limit = { low: 1.05, medium: 0.75, high: 0.52 };
  for (const q of ['low', 'medium', 'high']) {
    for (const fov of [50, 60, 68]) assert.ok(pixels(BARK_MIN_DIAMETER, TREE_MID[q], fov, 800) < limit[q], `${q} ${fov}`);
    assert.ok(pixels(0.046, SHRUB_REACH[q], 68, 800) < 0.85, q);
    assert.ok(pixels(0.021, SHRUB_REACH[q], 68, 800) < 0.5, q);
  }
  assert.ok(TREE_MID.low < TREE_MID.medium && TREE_MID.medium < TREE_MID.high);
  assert.ok(SHRUB_REACH.low < SHRUB_REACH.medium && SHRUB_REACH.medium < SHRUB_REACH.high);
  assert.equal(SHRUB_THIN, 8);
  assert.ok(Math.abs(pixels(1, 593, 68, 800) - 1) < 0.01); // 1 m at 593 m is one pixel at 68 degrees, 800 px
});
