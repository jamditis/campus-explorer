import { test } from 'node:test';
import assert from 'node:assert/strict';
import { crossings, cornersIn, edgesCross, outsidePart, ringDistance, snapQuantized, behind, planeLevel, splitEdge } from '../tools/web-export/cut.mjs';

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
  // in and out again across the L's cut-out quarter: two crossings, in order from the first point
  const u = crossings(4, 6, 6, 4.5, L);
  assert.equal(u.length, 2);
  assert.ok(u[0] < u[1]);
});

test('footprint corners inside a triangle are found, and nothing else', () => {
  assert.deepEqual(cornersIn(L, [4, 4], [7, 4], [4, 7]), [3]);
  assert.deepEqual(cornersIn(L, [1, 1], [2, 1], [1, 2]), []);
});

test('a triangle with one corner inside keeps the part outside, ending on the outline', () => {
  // corner 0 inside (9, 5); corners 1, 2 outside to the east
  const tri = [[9, 5], [11, 4], [11, 6]];
  const part = outsidePart(SQ, tri, [true, false, false], null);
  // polygon: crossing on 0-1, corner 1, corner 2, crossing on 2-0
  assert.deepEqual(part.map(p => p.kind), ['cross', 'corner', 'corner', 'cross']);
  for (const p of part.filter(q => q.kind === 'cross')) near(p.x, 10);
  // the crossing names its inside and outside corner, so two triangles that share the edge agree
  assert.deepEqual(part[0].edge, [0, 1]);
  assert.deepEqual(part[3].edge, [0, 2]);
});

test('a triangle with two corners inside keeps one small triangle', () => {
  const tri = [[9, 4], [12, 5], [9, 6]];
  const part = outsidePart(SQ, tri, [true, false, true], null);
  assert.deepEqual(part.map(p => p.kind), ['cross', 'corner', 'cross']);
});

test('a footprint corner inside the triangle goes between the two crossings', () => {
  // the L's reflex corner (5, 5) lies inside; corner 0 is inside the L, 1 and 2 are in the cut-out quarter
  const tri = [[4, 4], [8, 6], [6, 8]];
  const part = outsidePart(L, tri, [true, false, false], { index: 3, at: [5, 5] });
  assert.deepEqual(part.map(p => p.kind), ['cross', 'corner', 'corner', 'cross', 'ring']);
});

test('the kept part is a fan of triangles with the winding of the original, covering the outside', () => {
  const area = ps => ps.reduce((s, p, i) => {
    const q = ps[(i + 1) % ps.length];
    return s + p[0] * q[1] - q[0] * p[1];
  }, 0) / 2;
  const tri = [[4, 4], [8, 6], [6, 8]];
  const part = outsidePart(L, tri, [true, false, false], { index: 3, at: [5, 5] });
  const pts = part.map(p => [p.x, p.y]);
  // the part outside the L: the triangle (area 6) minus the bit inside the L
  const whole = area(tri);
  const kept = area(pts);
  assert.ok(kept > 0 && kept < whole, `${kept} of ${whole}`);
  // every point of the part is on or outside the L
  for (const [x, y] of pts) assert.ok(x >= 5 - 1e-9 && y >= 5 - 1e-9, `${x}, ${y}`);
});

test('a crossing can be pulled back along its edge toward the inside corner by an overlap', () => {
  const tri = [[9, 5], [11, 4], [11, 6]];
  const part = outsidePart(SQ, tri, [true, false, false], null, 0.1);
  for (const p of part.filter(q => q.kind === 'cross')) {
    near(Math.hypot(p.x - 10, p.y - 5 + (p.y < 5 ? 0.5 : -0.5)), 0.1, 1e-9);
    assert.ok(p.x < 10);
  }
});

test('a big triangle with no corner inside a footprint still meets it where the outline crosses it', () => {
  // a 100 m triangle over a 10 m square (the far-field ground over a scripted area): no corner inside
  assert.equal(cornersIn(SQ, [-50, -50], [60, -50], [5, 60]).length, 4);
  // a band of footprint across a triangle: no corner of either inside the other, two edges crossed
  const band = [[-10, 4], [20, 4], [20, 6], [-10, 6]];
  assert.ok(edgesCross(band, [[0, 0], [10, 0], [5, 10]]));
  assert.ok(!edgesCross(SQ, [[20, 20], [30, 20], [25, 30]]));
  assert.ok(!edgesCross(SQ, [[1, 1], [2, 1], [1, 2]])); // wholly inside: no crossing
});

// a far field quantised to 16 bits over 12.4 km (the north model's BD_farfield_3DEP): 0.378 m between grid points
const DIV = 32767, SCALE = 12375, STEP = SCALE / DIV;
// node units to the model frame (x east, y north, z up) for a node with only that scale: viewer y is up, z is minus north
const toModel = ([a, b, c]) => [a * SCALE, -c * SCALE, b * SCALE];
const local = (x, y, z) => [x / SCALE, z / SCALE, -y / SCALE];

test('the distance to an outline is to its nearest run, corners included', () => {
  near(ringDistance(SQ, 5, 5), 5);
  near(ringDistance(SQ, 12, 5), 2);
  near(ringDistance(SQ, 13, 14), 5); // to the corner (10, 10)
  near(ringDistance(L, 6, 6), 1); // the cut-out quarter: one metre from the reflex corner's runs
});

test('a cut vertex on a coarse grid is stored at a grid point inside the outline, never short of it', () => {
  const ring = [[100.13, 200.07], [180.41, 200.07], [180.41, 290.55], [100.13, 290.55]];
  const keep = (x, y) => x > 100.13 && x < 180.41 && y > 200.07 && y < 290.55 && ringDistance(ring, x, y) >= 0.01;
  let n = 0, short = 0;
  for (let k = 0; k < 400; k++) {
    // points on all four sides
    const t = k / 400, side = k % 4;
    const [x, y] = [[100.13 + 80 * t, 200.07], [180.41, 200.07 + 90 * t], [100.13 + 80 * t, 290.55], [100.13, 200.07 + 90 * t]][side];
    const q = local(x, y, 87.3), c = snapQuantized(q, DIV, toModel, keep);
    assert.ok(c.every(Number.isInteger));
    const [sx, sy, sz] = toModel(c.map(v => v / DIV));
    assert.ok(keep(sx, sy), `${x}, ${y} stored at ${sx}, ${sy}`);
    // no further than a grid diagonal and the margin from where it was cut
    const d = Math.hypot(sx - x, sy - y);
    assert.ok(d <= STEP * Math.SQRT2 + 0.01, `${d}`);
    near(sz, 87.3, STEP / 2 + 1e-9); // up is rounded to the nearest grid point
    // plain rounding (what the tiles had) leaves the vertex outside about half the time
    const [rx, ry] = toModel(q.map(v => Math.round(v * DIV) / DIV));
    if (!keep(rx, ry)) short++;
    n++;
  }
  assert.equal(n, 400);
  assert.ok(short > 100, `${short}`);
});

test('a cut vertex goes to the nearest grid point when no grid point near it is inside', () => {
  const q = local(50.02, 60.01, 80);
  const c = snapQuantized(q, DIV, toModel, () => false);
  assert.deepEqual(c, q.map(v => Math.round(v * DIV)));
});

test('a point behind an outline corner is inside both of its runs\' lines', () => {
  // the L's reflex corner (5, 5): inside the L near it, but in front of the corner along one run
  near(behind(L, 3, 4, 4), 1);
  assert.ok(behind(L, 3, 5.5, 4.9) < 0); // inside the L (below y 5) but east of the run x 5
  assert.ok(behind(L, 3, 4.9, 5.5) < 0); // inside the L (west of x 5) but north of the run y 5
  // a convex corner (10, 0) of the square, either winding
  near(behind(SQ, 1, 9, 1), 1);
  near(behind([...SQ].reverse(), 2, 9, 1), 1);
  assert.ok(behind(SQ, 1, 11, 1) < 0);
});

test('an outline corner cut into a coarse far field is stored behind both of its runs', () => {
  // the Village's reflex corner (-194, 741) on the skirt's 6 cm grid: stored inside the outline but in
  // front of one run, the far field's edge from it crossed the outline into the far field's wedge
  const S = 1980, D = 32767, toM = ([a, b, c]) => [a * S, -c * S, b * S];
  const ring = [[-191.26, 769.33], [-194.0, 741.0], [-182.79, 735.07], [-230, 700]];
  const q = [-194.0 / S, 111.25 / S, -741.0 / S];
  const c = snapQuantized(q, D, toM, (x, y) => behind(ring, 1, x, y) >= 0.01);
  const [x, y] = toM(c.map(v => v / D));
  assert.ok(behind(ring, 1, x, y) >= 0.01);
  assert.ok(Math.hypot(x + 194, y - 741) < 0.2);
});

test('a triangle with every corner inside a footprint can still be crossed by a notch of its outline', () => {
  // the Village's notch at (-200, 722): the outline comes in and goes out through the triangle's top edge
  const ring = [[-187.21, 720.93], [-200.88, 725.61], [-207.46, 708.76], [-205.6, 708.11], [-230, 760], [-180, 760]];
  const tri = [[-205.043, 725.014], [-205.043, 715.104], [-194.891, 725.014]];
  assert.deepEqual(cornersIn(ring, ...tri), []);
  assert.ok(edgesCross(ring, tri));
});

test('a corner moved off plain rounding takes the height of the ground it was cut from there', () => {
  // a far-field slope of 0.42 m a metre to the east, on the 0.38 m grid, cut by outlines of x 300.3 to 302.8
  const z = (x, y) => 120 - 0.42 * (x - 300) + 0.01 * (y - 650);
  const tri = [[290, 640], [320, 640], [300, 680]].map(([x, y]) => local(x, y, z(x, y)));
  const level = planeLevel(...tri, 1);
  near(level(local(305, 650, 0)) * SCALE, z(305, 650), 1e-6);
  let worst = 0, n = 0;
  for (let k = 0; k < 200; k++) {
    const y = 650 + k * 0.137, x = 300.3 + k * 0.0123;
    const keep = px => px < x - 0.01;
    const c = snapQuantized(local(x, y, z(x, y)), DIV, toModel, keep, 3, level);
    const [sx, sy, sz] = toModel(c.map(v => v / DIV));
    assert.ok(keep(sx, sy));
    const plain = local(x, y, z(x, y)).map(v => Math.round(v * DIV));
    if (c[0] === plain[0] && c[2] === plain[2]) continue; // not moved: rounded as before
    worst = Math.max(worst, Math.abs(sz - z(sx, sy))); n++;
  }
  assert.ok(n > 50, `${n}`);
  assert.ok(worst <= STEP / 2 + 1e-6, `${worst}`); // half a step off its own ground at most
});

test('a corner moved on a steep face keeps its rounded height', () => {
  // a near-vertical drop (the skirt's edge): 10 m a metre
  const z = x => 115 - 10 * (x - 300);
  const tri = [[299.9, 640], [300.1, 640], [300, 680]].map(([x, y]) => local(x, y, z(x)));
  const q = local(300.05, 650, z(300.05)), keep = px => px < 300.0;
  const c = snapQuantized(q, DIV, toModel, keep, 3, planeLevel(...tri, 1));
  near(toModel(c.map(v => v / DIV))[2], z(300.05), STEP / 2 + 1e-9);
});

test('the pieces the outline cut go to a primitive of their own, the rest stays', () => {
  // corners 0..3 were there before (n = 4); 4 and 5 were added: 4 on the outline, 5 a midpoint
  const keep = [0, 1, 2, 1, 4, 2, 2, 5, 3, 4, 5, 2];
  const { rest, edge } = splitEdge(keep, 4, new Set([0]));
  assert.deepEqual(rest, [0, 1, 2, 2, 5, 3]);
  assert.deepEqual(edge, [1, 4, 2, 4, 5, 2]);
});
