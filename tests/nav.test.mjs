import { test } from 'node:test';
import assert from 'node:assert/strict';
import { bearing, polyline, progress, pointAt, turns, turnWords, nextStep, roundDistance, arrowAngle } from '../viewer/nav-math.js';

const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`);

// north is -z, east is +x: walk 100 m north, then 50 m east (a right turn), then 30 m north (a left turn)
const L = polyline([[0, 0], [0, -100], [50, -100], [50, -130]]);

test('bearings in the viewer frame', () => {
  near(bearing(0, 0, 0, -1), 0, 1e-9, 'north');
  near(bearing(0, 0, 1, 0), 90, 1e-9, 'east');
  near(bearing(0, 0, 0, 1), 180, 1e-9, 'south');
  near(bearing(0, 0, -1, 0), 270, 1e-9, 'west');
});

test('progress along the line and the distance off it', () => {
  near(L.length, 180, 1e-9, 'length');
  const p = progress(L, 3, -40);
  near(p.s, 40, 1e-9, 's'); near(p.off, 3, 1e-9, 'off'); assert.equal(p.seg, 0);
  near(progress(L, 25, -104, 1, 100).s, 125, 1e-9, 'on the second leg');
  assert.deepEqual(pointAt(L, 110), [10, -100]);
  assert.deepEqual(pointAt(L, 999), [50, -130]);
});

test('progress does not jump back on a route that doubles back', () => {
  // out 50 m east and back 50 m west, 2 m to the side
  const U = polyline([[0, 0], [50, 0], [50, -2], [0, -2]]);
  near(progress(U, 10, -2, 2, 52).s, 52 + 40, 1e-9, 'on the way back');
});

test('noise near a later parallel stretch does not skip ahead', () => {
  // out 100 m north, 4 m east, back 100 m south: a fix 3 m east of the first leg is nearer the return leg
  const P = polyline([[0, 0], [0, -100], [4, -100], [4, 0]]);
  const p = progress(P, 3, -40, 0, 30);
  assert.equal(p.seg, 0); near(p.s, 40, 1e-9, 'still on the way out');
});

test('a right then a left close together are two turns', () => {
  const Z = polyline([[0, 0], [0, -50], [3, -50], [3, -100]]);
  const t = turns(Z);
  assert.equal(t.length, 2); assert.ok(t[0].angle > 0 && t[1].angle < 0);
});

test('turns and their words', () => {
  const t = turns(L);
  assert.equal(t.length, 2);
  near(t[0].s, 100, 1e-9, 'first'); near(t[0].angle, 90, 1e-9, 'right');
  near(t[1].angle, -90, 1e-9, 'left');
  assert.equal(turnWords(90), 'Turn right'); assert.equal(turnWords(-35), 'Slight left'); assert.equal(turnWords(160), 'Sharp right');
});

test('small wiggles are not turns and close bends add up', () => {
  const W = polyline([[0, 0], [0, -50], [3, -100], [3, -150]]);
  assert.equal(turns(W).length, 0);
  // two 45 degree bends 4 m apart make one right turn of 90
  const B = polyline([[0, 0], [0, -50], [2.83, -52.83], [6.83, -52.83], [56.83, -52.83]]);
  const t = turns(B);
  assert.equal(t.length, 1); near(t[0].angle, 90, 0.1, 'merged');
});

test('next step and arrival', () => {
  const t = turns(L);
  assert.deepEqual(nextStep(L, t, 20, 'Hall'), { text: 'Turn right', inM: 80, angle: 90 });
  const end = nextStep(L, t, 160, 'Hall');
  assert.equal(end.text, 'Arrive at Hall'); near(end.inM, 20, 1e-9, 'left');
});

test('distances read in round numbers', () => {
  assert.equal(roundDistance(2), '5 m');
  assert.equal(roundDistance(47), '45 m');
  assert.equal(roundDistance(234), '230 m');
  assert.equal(roundDistance(1260), '1.3 km');
});

test('the arrow turns from the view toward the route ahead', () => {
  near(arrowAngle(0, 0, 0, -10, 0), 0, 1e-9, 'ahead');
  near(arrowAngle(0, 0, 10, 0, 0), 90, 1e-9, 'to the right');
  near(arrowAngle(0, 0, 0, -10, 90), -90, 1e-9, 'facing east, route north: left');
});
