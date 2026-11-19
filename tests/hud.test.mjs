import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  metresPerPixel, niceScale, formatScale, formatElevation, mapExtent, worldToMap, mapToWorld,
  northOffset, northYaw, horizontalFov, headingLabel, toneMapToSrgb,
} from '../viewer/hud-math.js';

const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b} (tol ${tol})`);

test('metres per pixel follows the view frustum', () => {
  // 90° fov: the visible height at distance d is 2d
  near(metresPerPixel(100, 90, 800), 0.25, 1e-12, '90° fov');
  near(metresPerPixel(500, 50, 800), (2 * 500 * Math.tan(25 * Math.PI / 180)) / 800, 1e-12, '50° fov');
});

test('nice scale picks 1, 2 or 5 × 10^n and keeps the bar in range when it can', () => {
  for (let mpp = 0.002; mpp < 200; mpp *= 1.07) {
    const { metres, px } = niceScale(mpp);
    const lead = metres / 10 ** Math.floor(Math.log10(metres) + 1e-9);
    assert.ok([1, 2, 5].some(m => Math.abs(lead - m) < 1e-6), `round length ${metres}`);
    near(px, metres / mpp, 1e-6, 'px matches metres');
    // 1-2-5 steps can be 2.5× apart, so the 60-140 band is not always reachable; never far off it
    assert.ok(px >= 55 && px <= 150, `px ${px} for mpp ${mpp}`);
  }
  assert.deepEqual(niceScale(0.5), { metres: 50, px: 100 });
  assert.deepEqual(niceScale(0), { metres: 0, px: 0 });
});

test('labels', () => {
  assert.equal(formatScale(50), '50 m · 164 ft');
  assert.equal(formatScale(2), '2 m · 6.6 ft');
  assert.equal(formatScale(2000), '2 km · 1.24 mi');
  assert.equal(formatElevation(132.43), '132.4 m · 434 ft NAVD88 (model)');
  assert.equal(headingLabel(225, 'SW'), 'SW 225°');
  assert.equal(headingLabel(359.7, 'N'), 'N 0°');
});

test('map extent is a padded square and pixels round-trip', () => {
  const ext = mapExtent(-400, -300, 400, 100);
  near(ext.size, 840, 1e-9, 'size');
  near(ext.x0 + ext.size / 2, 0, 1e-9, 'centre x');
  near(ext.z0 + ext.size / 2, -100, 1e-9, 'centre z');
  const { u, v } = worldToMap(-400, -520, ext, 512);
  near(u, (20 / 840) * 512, 1e-9, 'west edge');
  near(v, 0, 1e-9, 'north edge is the top');
  const w = mapToWorld(123, 456, ext, 512), back = worldToMap(w.x, w.z, ext, 512);
  near(back.u, 123, 1e-9, 'u'); near(back.v, 456, 1e-9, 'v');
});

test('north-facing offsets look at true north', () => {
  const conv = 0.198;
  const { dx, dz } = northOffset(100, conv);
  near(Math.hypot(dx, dz), 100, 1e-9, 'distance kept');
  // view direction is -offset; grid bearing atan2(x, -z) must be -conv
  near(Math.atan2(-dx, dz) * 180 / Math.PI, -conv, 1e-9, 'orbit bearing');
  const yaw = northYaw(conv), fx = -Math.sin(yaw), fz = -Math.cos(yaw);
  near(Math.atan2(fx, -fz) * 180 / Math.PI + conv, 0, 1e-9, 'player true bearing');
});

test('horizontal fov', () => {
  near(horizontalFov(90, 1), 90, 1e-9, 'square');
  near(horizontalFov(50, 1.6), 2 * Math.atan(Math.tan(25 * Math.PI / 180) * 1.6) * 180 / Math.PI, 1e-9, 'wide');
});

test('tone mapping matches three.js ACES filmic then sRGB', () => {
  const out = [0, 0, 0];
  assert.deepEqual(toneMapToSrgb(0, 0, 0, 0.8, out), [0, 0, 0]);
  assert.deepEqual(toneMapToSrgb(100, 100, 100, 0.8, out), [255, 255, 255]);
  // mid grey stays mid grey-ish and ordering is kept
  const [r, g, b] = toneMapToSrgb(0.18, 0.18, 0.18, 0.8, out);
  assert.ok(r > 90 && r < 150 && Math.abs(r - g) <= 2 && Math.abs(g - b) <= 2, `grey ${r} ${g} ${b}`);
});
