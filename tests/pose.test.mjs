import test from 'node:test';
import assert from 'node:assert/strict';
import { landPose, inCampusBox, CLEARANCE } from '../viewer/pose-math.js';

const pose = (px, py, pz, tx, ty, tz) => ({ position: { x: px, y: py, z: pz }, target: { x: tx, y: ty, z: tz } });

test('a target set on a fallback height moves to the real ground, the view keeps its framing', () => {
  // the lookup missed (tiles not in yet) and used the campus floor, 30 m below the real ground
  const p = landPose(pose(0, 160, 50, 0, 120, 0), 150, 152);
  assert.deepEqual(p.target, { x: 0, y: 150, z: 0 });
  assert.deepEqual(p.position, { x: 0, y: 190, z: 50 });
});

test('a camera below the ground under it is lifted above it', () => {
  // the target is right, but the ground rises behind the target, above the camera
  const p = landPose(pose(0, 125, 80, 0, 120, 0), 120, 140);
  assert.deepEqual(p.target, { x: 0, y: 120, z: 0 });
  assert.equal(p.position.y, 140 + CLEARANCE);
});

test('a camera inside a roof is lifted above the roof', () => {
  const p = landPose(pose(0, 160, 30, 0, 150, 0), 150, 165); // the highest surface under the camera is a roof at 165
  assert.equal(p.position.y, 165 + CLEARANCE);
});

test('a good pose is left alone, and unknown ground changes nothing', () => {
  assert.equal(landPose(pose(0, 190, 50, 0, 150, 0), 150, 152), null);
  assert.equal(landPose(pose(0, 190, 50, 0, 150, 0), null, null), null);
  assert.equal(landPose(pose(0, 190, 50, 0, 150.2, 0), 150, 152), null); // within a few centimetres: no nudge
});

test('the target keeps its ground when only the camera ground is known', () => {
  const p = landPose(pose(0, 125, 80, 0, 120, 0), null, 140);
  assert.deepEqual(p.target, { x: 0, y: 120, z: 0 });
  assert.equal(p.position.y, 140 + CLEARANCE);
});

test('far-field ground does not count toward the campus box (it reaches 190 m below the campus)', () => {
  // BD_farfield_3DEP_ortho in n_t_0_0.glb: 2.3 km across, down to y -54
  assert.equal(inCampusBox({ x: 2400, y: 600, z: 2300 }), false);
  assert.equal(inCampusBox({ x: 300, y: 40, z: 500 }), true);
  assert.equal(inCampusBox({ x: 900, y: 5, z: 120 }), true);
});
