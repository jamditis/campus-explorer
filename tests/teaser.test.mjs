import test from 'node:test';
import assert from 'node:assert/strict';
import {
  ease, cruise, catmull, spline, timeline, frameAt, cameraAt, presence, dimension, wipeShaft,
  faceYaw, textWidth, layout, stagger,
} from '../tools/teaser/path.mjs';

const near = (a, b, e = 1e-6) => assert.ok(Math.abs(a - b) <= e, `${a} vs ${b}`);

test('eases start at 0, end at 1 and are flat at the ends', () => {
  for (const name of ['smooth', 'smoother', 'sine']) {
    const f = ease[name];
    near(f(0), 0); near(f(1), 1); near(f(0.5), 0.5);
    near((f(0.001) - f(0)) / 0.001, 0, 0.01); near((f(1) - f(0.999)) / 0.001, 0, 0.01);
  }
  assert.ok(ease.back(0.7) > 1, 'back overshoots'); near(ease.back(1), 1); near(ease.back(0), 0);
});

test('cruise is monotone with continuous speed and no corners', () => {
  let prev = 0, prevV = 0;
  for (let i = 1; i <= 1000; i++) {
    const t = i / 1000, d = cruise(t, 0.25, 0.35), v = (d - prev) * 1000;
    assert.ok(d >= prev - 1e-12);
    if (i > 1) assert.ok(Math.abs(v - prevV) < 0.02, `speed jumps at ${t}`);
    prev = d; prevV = v;
  }
  near(cruise(0), 0); near(cruise(1), 1);
  near(cruise(0.5, 0, 0), 0.5); // no ramps: constant speed
});

test('catmull passes through its middle points', () => {
  const p = [[0, 0], [1, 0], [2, 1], [3, 1]];
  assert.deepEqual(catmull(...p, 0).map(v => +v.toFixed(9)), [1, 0]);
  assert.deepEqual(catmull(...p, 1).map(v => +v.toFixed(9)), [2, 1]);
});

test('spline is walked by length: equal steps of s give equal steps of distance', () => {
  const s = spline([[0, 0, 0], [10, 0, 0], [12, 0, 0], [40, 0, 0]]);
  near(s.length, 40, 1e-3);
  near(s.at(0.25)[0], 10, 0.05); near(s.at(0.5)[0], 20, 0.05); near(s.at(1)[0], 40, 1e-6);
  const c = spline([[0, 0], [10, 10], [20, 0]]);
  near(c.at(0)[0], 0); near(c.at(1)[0], 20, 1e-6);
});

test('frames map to shots and local time', () => {
  const shots = [{ duration: 2 }, { duration: 1.5 }];
  assert.deepEqual(timeline(shots, 30), { starts: [0, 60], frames: 105 });
  assert.deepEqual(frameAt(0, shots, 30), { shot: 0, t: 0, sec: 0 });
  assert.equal(frameAt(59, shots, 30).t, 1);
  assert.equal(frameAt(60, shots, 30).shot, 1);
  assert.equal(frameAt(105, shots, 30), null);
});

test('camera at the ends of a shot is at its first and last keys', () => {
  const shot = { duration: 4, pos: [[0, 10, 0], [50, 12, 0], [100, 10, 0]], look: [[0, 0, -50], [100, 0, -50]], fov: 40, fov2: 30 };
  const a = cameraAt(shot, 0), b = cameraAt(shot, 1);
  assert.deepEqual(a.pos.map(Math.round), [0, 10, 0]); assert.deepEqual(b.pos.map(Math.round), [100, 10, 0]);
  near(a.fov, 40); near(b.fov, 30);
});

test('presence rises with an overshoot, holds and leaves', () => {
  const g = { in: 1, inDur: 0.5, out: 4, outDur: 0.5 };
  near(presence(g, 0.5).on, 0); near(presence(g, 2).on, 1); near(presence(g, 4).on, 0);
  assert.ok(presence(g, 1.4).on > 1); // overshoot on the way in
});

test('a dimension line keeps its arrow tips on the end points and its shaft between the heads', () => {
  const d = dimension([0, 0, 0], [100, 0, 0], { head: 4 });
  near(d.length, 100);
  assert.deepEqual(d.heads[0][0], [0, 0, 0]); assert.deepEqual(d.heads[1][0], [100, 0, 0]);
  near(d.shaft[0][0], 4); near(d.shaft[1][0], 96);
  near(d.side[1], 1); // vertical plane: the heads open up and down
  const flat = dimension([0, 0, 0], [0, 0, -50], { up: [1, 0, 0] });
  near(flat.side[0], 1); near(flat.side[1], 0);
  const half = wipeShaft(d.shaft, 0.5);
  near(half[0][0], 27); near(half[1][0], 73);
});

test('text placement: yaw, width, centred layout, stagger', () => {
  near(faceYaw([0, 0, 0], [0, 0, 10]), 0); near(faceYaw([0, 0, 0], [10, 0, 0]), Math.PI / 2);
  const glyphs = { a: { adv: 0.5 }, b: { adv: 0.7 } };
  near(textWidth('ab', glyphs), 1.2); near(textWidth('ab', glyphs, 0.1), 1.3);
  const l = layout('ab', glyphs);
  near(l.chars[0].x, -0.6); near(l.chars[1].x, -0.1);
  near(stagger(0, 0, 3), 0); near(stagger(1, 2, 3), 1); near(stagger(0.5, 2, 3), 0);
});
