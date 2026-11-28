import test from 'node:test';
import assert from 'node:assert/strict';
import { doorFrom, wantsOpen, stepOpen, leafMove, toViewer, DOOR_NEAR, DOOR_FAR, DOOR_TIME } from '../viewer/doors-math.js';

const apply = (m, [x, y, z]) => [m[0] * x + m[4] * y + m[8] * z + m[12], m[1] * x + m[5] * y + m[9] * z + m[13], m[2] * x + m[6] * y + m[10] * z + m[14]];
const near = (a, b) => a.every((v, i) => Math.abs(v - b[i]) < 1e-6);

test('door extras in Blender axes become viewer axes, and broken extras are no door', () => {
  assert.deepEqual(toViewer([1, 2, 3]), [1, 3, -2]);
  const d = doorFrom({ id: 'ccom_main', building: 'ccom', kind: 'swing', hinge: [10, 20, 130], axis: [0, 0, 2], open: 90 });
  assert.deepEqual(d.hinge, [10, 130, -20]); assert.deepEqual(d.axis, [0, 1, 0]); assert.equal(d.open, Math.PI / 2);
  assert.deepEqual(doorFrom({ id: 's', kind: 'slide', travel: [1.2, 0, 0] }).travel, [1.2, 0, 0]);
  assert.equal(doorFrom({ id: 'x', kind: 'swing', hinge: [0, 0, 0], axis: [0, 0, 0], open: 90 }), null);
  assert.equal(doorFrom({ id: 'x', kind: 'swing', hinge: [0, 0], axis: [0, 0, 1], open: 90 }), null);
  assert.equal(doorFrom({ kind: 'slide', travel: [1, 0, 0] }), null);
  assert.equal(doorFrom(null), null);
});

test('a door opens for a walker near it who faces it, and stays open until they are further away', () => {
  const at = { x: 0, y: 100, z: 0 };
  assert.equal(wantsOpen(at, { x: 0, y: 100, z: 2.5 }, { x: 0, z: -1 }, false), true); // 2.5 m away, looking at it
  assert.equal(wantsOpen(at, { x: 0, y: 100, z: 2.5 }, { x: 0, z: 1 }, false), false); // walking away
  assert.equal(wantsOpen(at, { x: 0, y: 100, z: DOOR_NEAR + 0.1 }, { x: 0, z: -1 }, false), false);
  assert.equal(wantsOpen(at, { x: 0, y: 100, z: 4 }, { x: 0, z: 1 }, true), true); // open: stays until DOOR_FAR
  assert.equal(wantsOpen(at, { x: 0, y: 100, z: DOOR_FAR + 0.1 }, { x: 0, z: 1 }, true), false);
  assert.equal(wantsOpen(at, { x: 0, y: 104, z: 1 }, { x: 0, z: -1 }, false), false); // a floor above
  assert.equal(wantsOpen(at, { x: 0.2, y: 100, z: 0.2 }, { x: 0, z: 1 }, false), true); // in the doorway
});

test('opening takes DOOR_TIME seconds and stops at shut and fully open', () => {
  assert.equal(stepOpen(0, true, DOOR_TIME / 2), 0.5);
  assert.equal(stepOpen(0.9, true, DOOR_TIME), 1);
  assert.equal(stepOpen(0.1, false, DOOR_TIME), 0);
});

test('a swing leaf turns about its hinge line, a sliding leaf moves along its travel', () => {
  const d = doorFrom({ id: 'a', kind: 'swing', hinge: [5, 0, 0], axis: [0, 0, 1], open: 90 }); // hinge at x 5, vertical
  assert.ok(near(apply(leafMove(d, 0), [6, 1, 0]), [6, 1, 0])); // shut: nothing moves
  assert.ok(near(apply(leafMove(d, 1), [5, 3, 0]), [5, 3, 0])); // the hinge stays
  // 90 degrees about viewer +y (Blender +z): a point 1 m east of the hinge ends 1 m north (-z)
  assert.ok(near(apply(leafMove(d, 1), [6, 1, 0]), [5, 1, -1]));
  const half = apply(leafMove(d, 0.5), [6, 1, 0]); // eased: half way in time is half way in angle
  assert.ok(near(half, [5 + Math.SQRT1_2, 1, -Math.SQRT1_2]));
  const s = doorFrom({ id: 'b', kind: 'slide', travel: [1.2, 0, 0] });
  assert.ok(near(apply(leafMove(s, 1), [0, 0, 0]), [1.2, 0, 0]));
  assert.ok(near(apply(leafMove(s, 0.5), [0, 0, 0]), [0.6, 0, 0]));
});
