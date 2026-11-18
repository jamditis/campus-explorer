import test from 'node:test';
import assert from 'node:assert/strict';
import { applyDeadZone, clampUnit, keysToAxes, stickFromTouch } from '../viewer/input.js';

const close = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) < eps, `${a} != ${b}`);

test('dead zone: inside and on the edge gives zero', () => {
  assert.deepEqual(applyDeadZone(0, 0, 0.15), [0, 0]);
  assert.deepEqual(applyDeadZone(0.1, 0.1, 0.15), [0, 0]);
  assert.deepEqual(applyDeadZone(0.15, 0, 0.15), [0, 0]);
});

test('dead zone: output starts at zero just past the edge and rescales', () => {
  const [x] = applyDeadZone(0.151, 0, 0.15);
  assert.ok(x > 0 && x < 0.01);
  const [hx, hy] = applyDeadZone(0, -0.575, 0.15);
  close(hx, 0);
  close(hy, -0.5);
  const [fx, fy] = applyDeadZone(1, 0, 0.15);
  close(fx, 1);
  close(fy, 0);
});

test('dead zone: keeps direction and never exceeds length 1', () => {
  const [x, y] = applyDeadZone(1, 1, 0.15);
  close(Math.hypot(x, y), 1);
  close(x, y);
});

test('clampUnit leaves short vectors and shortens long diagonals', () => {
  assert.deepEqual(clampUnit(0.3, -0.4), [0.3, -0.4]);
  const [x, z] = clampUnit(1, 1);
  close(Math.hypot(x, z), 1);
  close(x, Math.SQRT1_2);
});

test('keys: W and D move forward and right, diagonal clamped', () => {
  const a = keysToAxes(new Set(['KeyW', 'KeyD']), 'walk');
  close(Math.hypot(a.moveX, a.moveZ), 1);
  assert.ok(a.moveX > 0 && a.moveZ > 0);
  const b = keysToAxes(new Set(['ArrowUp']), 'walk');
  assert.equal(b.moveZ, 1);
  assert.equal(b.moveX, 0);
});

test('keys: opposite keys cancel', () => {
  const a = keysToAxes(new Set(['KeyW', 'KeyS', 'KeyA', 'ArrowRight']), 'fly');
  assert.equal(a.moveX, 0);
  assert.equal(a.moveZ, 0);
  const b = keysToAxes(new Set(['Space', 'KeyQ']), 'fly');
  assert.equal(b.rise, 0);
});

test('keys: shift sets run', () => {
  assert.equal(keysToAxes(new Set(['ShiftLeft']), 'walk').run, true);
  assert.equal(keysToAxes(new Set(['ShiftRight', 'KeyW']), 'fly').run, true);
  assert.equal(keysToAxes(new Set(['KeyW']), 'fly').run, false);
});

test('keys: rise keys work in fly mode only', () => {
  assert.equal(keysToAxes(new Set(['Space']), 'fly').rise, 1);
  assert.equal(keysToAxes(new Set(['KeyE']), 'fly').rise, 1);
  assert.equal(keysToAxes(new Set(['KeyQ']), 'fly').rise, -1);
  assert.equal(keysToAxes(new Set(['KeyC']), 'fly').rise, -1);
  for (const code of ['Space', 'KeyE', 'KeyQ', 'KeyC']) {
    assert.equal(keysToAxes(new Set([code]), 'walk').rise, 0);
  }
});

test('stick: up is forward, right is right, clamped to the ring', () => {
  const up = stickFromTouch(0, -28, 56);
  close(up.moveZ, 0.5);
  close(up.moveX, 0);
  const far = stickFromTouch(200, 0, 56);
  close(far.moveX, 1);
  close(far.amount, 1);
  close(far.knobX, 56);
  const none = stickFromTouch(0, 0, 56);
  assert.equal(none.amount, 0);
  assert.equal(none.moveX, 0);
});
