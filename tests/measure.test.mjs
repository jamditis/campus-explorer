import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  isClick, gridBearing, trueBearing, pathTotals, formatRise, formatSlope, formatBearing,
} from '../viewer/measure-math.js';
import { convergenceDeg, CAMPUS } from '../viewer/geo.js';

const near = (a, b, tol = 1e-9, msg = '') => assert.ok(Math.abs(a - b) <= tol, `${msg} ${a} vs ${b}`);

test('click versus drag', () => {
  assert.equal(isClick({ x: 10, y: 10, t: 0 }, { x: 13, y: 13, t: 200 }), true);
  assert.equal(isClick({ x: 10, y: 10, t: 0 }, { x: 15, y: 10, t: 100 }), false, '5 px is a drag');
  assert.equal(isClick({ x: 10, y: 10, t: 0 }, { x: 10, y: 10, t: 400 }), false, '400 ms is a hold');
});

test('grid bearing: -Z is north, +X is east', () => {
  const o = { x: 0, y: 0, z: 0 };
  near(gridBearing(o, { x: 0, z: -5 }), 0);
  near(gridBearing(o, { x: 5, z: 0 }), 90);
  near(gridBearing(o, { x: 0, z: 5 }), 180);
  near(gridBearing(o, { x: -5, z: 0 }), 270);
});

test('true bearing adds the grid convergence', () => {
  const conv = convergenceDeg(CAMPUS.lat, CAMPUS.lon);
  near(trueBearing({ x: 0, z: 0 }, { x: 10, z: 0 }), 90 + conv, 1e-3);
});

test('totals for two points', () => {
  const t = pathTotals([{ x: 0, y: 100, z: 0 }, { x: 30, y: 103, z: -40 }]);
  near(t.horizontal, 50); near(t.rise, 3); near(t.slope, 6);
  near(t.straight, Math.hypot(50, 3)); near(t.path, t.straight);
  assert.equal(t.segments.length, 1);
  assert.ok(t.bearing > 36 && t.bearing < 37.5);
});

test('totals for a path', () => {
  const t = pathTotals([{ x: 0, y: 0, z: 0 }, { x: 3, y: 0, z: 4 }, { x: 3, y: -2, z: 4 }]);
  assert.deepEqual(t.segments, [5, 2]);
  near(t.path, 7); near(t.straight, Math.hypot(5, 2)); near(t.horizontal, 5); near(t.rise, -2);
  assert.equal(t.slope, null, 'slope only for two points');
  assert.equal(t.bearing, null);
});

test('degenerate paths', () => {
  assert.equal(pathTotals([]).path, 0);
  const one = pathTotals([{ x: 1, y: 2, z: 3 }]);
  assert.equal(one.count, 1); assert.equal(one.straight, 0);
  const plumb = pathTotals([{ x: 0, y: 0, z: 0 }, { x: 0, y: 5, z: 0 }]);
  assert.equal(plumb.slope, null); assert.equal(plumb.bearing, null); near(plumb.straight, 5);
});

test('formatting', () => {
  assert.equal(formatRise(2.4), '+2.4 m · +7.9 ft');
  assert.equal(formatRise(-0.6), '−0.6 m · −2.0 ft');
  assert.equal(formatRise(0.01), '0.0 m · 0.0 ft');
  assert.equal(formatSlope(6), '+6.0 %');
  assert.equal(formatSlope(-12.34), '−12.3 %');
  assert.equal(formatSlope(250), '+250 %');
  assert.equal(formatSlope(null), '');
  assert.equal(formatBearing(123.4), '123° ESE');
  assert.equal(formatBearing(359.7), '0° N');
});
