import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bearing, profile, simplify, curtain, beyond } from '../tools/web-export/skyline.mjs';

const near = (a, b, tol = 1e-9) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);
const EYE = [0, 0, 100];
// a box (two side walls facing the eye are enough for a profile) as triangles, model frame: x east, y north, z up
function wall(x0, y0, x1, y1, z0, z1) {
  return [x0, y0, z0, x1, y1, z0, x1, y1, z1, x0, y0, z0, x1, y1, z1, x0, y0, z1];
}

test('bearing is clockwise from grid north, in degrees from 0 to 360', () => {
  near(bearing(0, 1), 0);
  near(bearing(1, 0), 90);
  near(bearing(0, -1), 180);
  near(bearing(-1, 0), 270);
  near(bearing(1, 1), 45);
});

test('a wall due east gives its top elevation in the bins it covers and nothing elsewhere', () => {
  // wall 10 km east, from bearing ~87.1 to ~92.9 degrees, top at z 300 (200 m over the eye)
  const p = profile(new Float32Array(wall(10000, 500, 10000, -500, 0, 300)), EYE, 0.5);
  const at = b => Math.floor(b / 0.5);
  const e = Math.atan2(200, 10000) * 180 / Math.PI;
  near(p.e[at(90)], e, 1e-4); // straight ahead: the wall's own top
  assert.ok(p.e[at(88)] > e - 0.01 && p.e[at(88)] < e); // to the side the top is a bit farther, a bit lower
  assert.equal(p.e[at(80)], -Infinity);
  assert.equal(p.e[at(270)], -Infinity);
  near(p.r[at(90)], 10000, 1); // where the top is
  near(p.z[at(90)], 300, 1e-3);
  near(p.zMin, 0);
});

test('a nearer tall tower in front of a far low block wins its bins', () => {
  const tris = [
    ...wall(20000, 2000, 20000, -2000, 0, 150), // far block, 50 m over the eye at 20 km
    ...wall(10000, 30, 10000, -30, 0, 400), // tower at 10 km, 300 m over the eye
  ];
  const p = profile(new Float32Array(tris), EYE, 0.05);
  const i = Math.floor(90 / 0.05);
  near(p.r[i], 10000, 1);
  near(p.z[i], 400, 1e-3);
  near(p.r[Math.floor(85 / 0.05)], 20000 / Math.cos(5 * Math.PI / 180), 2);
});

test('a tower narrower than a bin is not lost between bin centres', () => {
  // 10 m wide at 20 km: 0.03 degrees, less than the 0.05 degree bin
  const p = profile(new Float32Array(wall(20000, 5.01, 20000, -4.99, 0, 500)), EYE, 0.05);
  const hit = [...p.e].filter(v => v > -Infinity);
  assert.ok(hit.length >= 1 && hit.length <= 2);
  near(Math.max(...hit), Math.atan2(400, 20000) * 180 / Math.PI, 1e-3);
});

test('triangles that straddle north keep both sides of 0 degrees', () => {
  const p = profile(new Float32Array(wall(-500, 10000, 500, 10000, 0, 300)), EYE, 0.5);
  assert.ok(p.e[0] > 0); // bin 0..0.5
  assert.ok(p.e[p.e.length - 1] > 0); // bin 359.5..360
  assert.equal(p.e[Math.floor(180 / 0.5)], -Infinity);
});

test('simplify keeps the ends and peaks of each run and drops points within the height tolerance', () => {
  const e = Float64Array.from([-Infinity, 1, 1, 1, 1, 5, 1, 1, -Infinity, -Infinity, 2, 2]);
  const runs = simplify({ e, step: 1 }, 0.1);
  assert.deepEqual(runs, [[1, 4, 5, 6, 7], [10, 11]]);
  // a slope within the tolerance collapses to its ends
  const s = simplify({ e: Float64Array.from([1, 2.01, 3, 3.99, 5, 6]), step: 1 }, 0.05);
  assert.deepEqual(s, [[0, 5]]);
});

test('a run that wraps past 360 degrees is one run', () => {
  const e = Float64Array.from([2, 2, -Infinity, -Infinity, 2, 2]);
  assert.deepEqual(simplify({ e, step: 60 }, 0.1), [[4, 1]]);
});

test('the curtain stands at the profile points, from the lowest source height to their tops', () => {
  const p = profile(new Float32Array(wall(10000, 500, 10000, -500, -20, 300)), EYE, 0.5);
  const runs = simplify(p, 0.01);
  const c = curtain(runs, p, EYE);
  const k = runs[0].length;
  assert.equal(c.position.length, k * 2 * 3);
  assert.equal(c.index.length, (k - 1) * 6);
  for (let v = 0; v < k * 2; v++) {
    const [x, y, z] = c.position.slice(v * 3, v * 3 + 3);
    near(x, 10000, 0.5); // on the wall plane (a top point is where the ray meets the wall)
    assert.ok(Math.abs(y) <= 501);
    assert.ok(v % 2 ? Math.abs(z + 20) < 1e-3 : Math.abs(z - 300) < 1e-3); // top, then bottom
    // normal faces the eye, level
    near(c.normal[v * 3 + 2], 0);
    assert.ok(c.normal[v * 3] < -0.99);
  }
});

test('beyond: a mesh counts as super distant only when all its corners are past the distance in plan', () => {
  assert.equal(beyond(wall(10500, -300, 12000, 400, 0, 50), 10000), true);
  assert.equal(beyond(wall(9000, 5000, 12000, 6000, 0, 50), 10000), true); // nearest corner 10.3 km
  assert.equal(beyond(wall(-2000, 0, 25000, 0, 0, 50), 10000), false); // reaches the campus
  assert.equal(beyond(wall(9000, -100, 9500, 100, 0, 50), 10000), false);
  // towers on an arc 12 km out: their box reaches within 9 km, their corners do not
  assert.equal(beyond([...wall(12000, 0, 12000, 10, 0, 50), ...wall(0, -12000, 10, -12000, 0, 50)], 10000), true);
  assert.equal(beyond([], 10000), false);
});

test('with a reach, points past it come nearer along their sight line: same bearing and elevation from the eye', () => {
  const p = profile(new Float32Array(wall(22000, 500, 22000, -500, -40, 400)), EYE, 0.5);
  const runs = simplify(p, 0.01);
  const far = curtain(runs, p, EYE), pulled = curtain(runs, p, EYE, 17000);
  for (let v = 0; v < far.position.length / 3; v++) {
    const [x, y, z] = far.position.slice(v * 3, v * 3 + 3), [a, b, c] = pulled.position.slice(v * 3, v * 3 + 3);
    near(Math.hypot(a, b), 17000, 1e-3 * 17000);
    near(Math.atan2(b, a), Math.atan2(y, x), 1e-6);
    near(Math.atan2(c - EYE[2], Math.hypot(a, b)), Math.atan2(z - EYE[2], Math.hypot(x, y)), 1e-6);
  }
  // nearer than the reach: unchanged
  const q = profile(new Float32Array(wall(12000, 500, 12000, -500, -40, 400)), EYE, 0.5);
  assert.deepEqual(curtain(simplify(q, 0.01), q, EYE, 17000).position, curtain(simplify(q, 0.01), q, EYE).position);
});
