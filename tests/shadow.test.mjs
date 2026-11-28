import test from 'node:test';
import assert from 'node:assert/strict';
import { SHADOW_SLACK, shadowHalf, shadowReach, shadowMoves } from '../viewer/shadow-math.js';

test('the shadow area is 0.9 x the view distance, 45 to 700 m, in steps of 1.25', () => {
  assert.equal(shadowHalf(0), 45);
  assert.equal(shadowHalf(50), 45);
  assert.equal(+shadowHalf(60).toFixed(3), 56.25);
  assert.ok(shadowHalf(5000) <= 700 * 1.13 && shadowHalf(5000) >= 700 / 1.13);
  assert.equal(shadowReach(64), 64 * (1 + SHADOW_SLACK));
});

test('the box stays while the focus drifts inside the slack, and moves past it', () => {
  const last = { x: 0, y: 100, z: 0 }, half = 48, slack = half * SHADOW_SLACK; // 3 m
  assert.equal(shadowMoves({ x: 2.9, y: 100, z: -2.9 }, last, half, half, false), false);
  assert.equal(shadowMoves({ x: 3.1, y: 100, z: 0 }, last, half, half, false), true);
  assert.equal(shadowMoves({ x: 0, y: 100, z: -slack - 0.01 }, last, half, half, false), true);
});

test('the box moves at first, with a new size or height step, and whenever the map is redrawn anyway', () => {
  const f = { x: 1, y: 100, z: 1 }, last = { x: 0, y: 100, z: 0 };
  assert.equal(shadowMoves(f, null, 45, 0, false), true);
  assert.equal(shadowMoves(f, last, 56.25, 45, false), true);
  assert.equal(shadowMoves({ ...f, y: 104 }, last, 45, 45, false), true);
  assert.equal(shadowMoves(f, last, 45, 45, true), true);
});

test('wherever the focus sits in the slack, the shadow camera still covers the whole area around it', () => {
  for (const half of [45, 140, 700]) {
    const drift = half * SHADOW_SLACK;
    assert.ok(drift + half <= shadowReach(half) + 1e-9);
  }
});
