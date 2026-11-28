import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  DECLINATION, wrap360, angleDiff, phoneView, compassOf, easeAngle, yawForBearing, createTrack, campusCheck,
} from '../viewer/follow-math.js';

const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`);

test('angles wrap and take the short way round', () => {
  assert.equal(wrap360(-10), 350);
  assert.equal(angleDiff(350, 10), 20);
  assert.equal(angleDiff(10, 350), -20);
  near(easeAngle(350, 10, 10), 10, 1e-6, 'eases across north');
  assert.equal(easeAngle(null, 370, 0.016), 10);
});

// W3C DeviceOrientation spec, section on the device coordinate frame: alpha = beta = gamma = 0 is the phone
// flat, screen up, top edge to north; beta = 90 stands it upright with the back facing that way.
test('phone held upright looks out of its back', () => {
  const v = phoneView(0, 90, 0);
  near(v.heading, 0, 1e-9, 'north'); near(v.pitch, 0, 1e-9, 'level'); assert.equal(v.flat, false);
  // alpha counts counterclockwise, so alpha 90 turns the phone to face west
  near(phoneView(90, 90, 0).heading, 270, 1e-9, 'west');
  near(phoneView(270, 90, 0).heading, 90, 1e-9, 'east');
  // tilted back 30 degrees past upright looks 30 degrees up
  near(phoneView(0, 120, 0).pitch, 30, 1e-9, 'up');
  near(phoneView(0, 60, 0).pitch, -30, 1e-9, 'down');
});

test('phone held flat takes its heading from the top edge', () => {
  const v = phoneView(90, 0, 0);
  assert.equal(v.flat, true); near(v.heading, 270, 1e-9, 'top to west'); near(v.pitch, -90, 1e-9, 'back to ground');
});

test('compass readings from iOS and Android events', () => {
  assert.equal(compassOf({ webkitCompassHeading: 42, alpha: 7 }), 42);
  assert.equal(compassOf({ absolute: true, alpha: 90 }), 270);
  assert.equal(compassOf({ absolute: false, alpha: 90 }), null);
  assert.equal(compassOf({ webkitCompassHeading: -1, absolute: false, alpha: 3 }), null);
  assert.ok(DECLINATION < -12 && DECLINATION > -13);
});

test('yaw for a bearing matches the walk camera basis', () => {
  // the walk camera looks along (-sin yaw, 0, -cos yaw); -z is grid north, +x east
  for (const b of [0, 45, 90, 200]) {
    const yaw = yawForBearing(b, 0);
    const dx = -Math.sin(yaw), dz = -Math.cos(yaw);
    near(wrap360(Math.atan2(dx, -dz) * 180 / Math.PI), b, 1e-9, `bearing ${b}`);
  }
  // grid north sits east of true north, so a true bearing is a smaller grid bearing
  near(yawForBearing(10, 0.2), -(9.8 * Math.PI / 180), 1e-12, 'convergence');
});

test('track smooths jitter and follows a steady walk', () => {
  // deterministic jitter (no clock or randomness): ±4 m around a walker going east at 1.4 m/s
  const t = createTrack();
  const jitter = [3, -4, 2, -1, 4, -3, 1, -2, 3, -4, 0, 2];
  let s;
  for (let i = 0; i < 60; i++) s = t.add(i, 1.4 * i + jitter[i % 12], jitter[(i + 5) % 12], 5);
  near(s.x, 1.4 * 59, 3, 'x within 3 m of truth');
  near(s.z, 0, 3, 'z within 3 m');
  near(s.vx, 1.4, 0.6, 'speed');
  assert.ok(s.sigma < 5, 'more certain than one fix');
});

test('track starts over after a long gap', () => {
  const t = createTrack();
  t.add(0, 0, 0, 5);
  const s = t.add(100, 500, 0, 5);
  assert.equal(s.x, 500);
});

test('campus check grows the box by a margin', () => {
  const box = { x0: -100, x1: 100, z0: -100, z1: 100 };
  assert.deepEqual(campusCheck(0, 0, box), { on: true, distance: 0 });
  assert.equal(campusCheck(240, 0, box).on, true);
  const off = campusCheck(1250, 0, box);
  assert.equal(off.on, false); near(off.distance, 1000, 1e-9, 'distance');
});
