import { test } from 'node:test';
import assert from 'node:assert/strict';
import { SHOTS, poseAt, ease, letterbox, lightOffset } from '../viewer/cinema-math.js';
import { flightLimit, clampToLimit } from '../viewer/flight-math.js';
import { readFileSync } from 'node:fs';

test('ease starts and ends at rest', () => {
  assert.equal(ease(0), 0); assert.equal(ease(1), 1); assert.equal(ease(-1), 0); assert.equal(ease(2), 1);
  assert.equal(ease(0.5), 0.5);
  const d = 1e-4;
  assert.ok((ease(d) - ease(0)) / d < 1e-6 && (ease(1) - ease(1 - d)) / d < 1e-6);
});

test('every shot runs from its first pose to its last, over the ground it names', () => {
  for (const s of SHOTS) {
    const a = poseAt(s, 0, 100), b = poseAt(s, s.seconds, 100), y = s.ground ? 100 : 0;
    assert.deepEqual(a.position, [s.from.position[0], s.from.position[1] + y, s.from.position[2]]);
    assert.deepEqual(b.target, [s.to.target[0], s.to.target[1] + y, s.to.target[2]]);
    assert.deepEqual(poseAt(s, 0, 100, true), b, 'reduced motion holds the last pose');
    assert.ok(s.caption && s.seconds > 2 && (lightOffset(s) === null || Math.abs(lightOffset(s)) <= 180));
  }
});

test('orbit mode can show every frame: the target is below the camera and the camera inside the flight limit', () => {
  const manifest = JSON.parse(readFileSync(new URL('../models/main/manifest.json', import.meta.url)));
  const limit = flightLimit(manifest.tiles, { skirtHalf: manifest.landcover?.half ?? 2000, floorY: 100 });
  for (const s of SHOTS) for (let k = 0; k <= 10; k++) {
    const p = poseAt(s, (s.seconds * k) / 10, 130);
    assert.ok(p.target[1] < p.position[1], `${s.caption} at ${k}/10`);
    const c = clampToLimit({ x: p.position[0], y: p.position[1], z: p.position[2] }, limit);
    assert.deepEqual([c.x, c.y, c.z], p.position, `${s.caption} at ${k}/10 inside the limit`);
  }
});

test('letterbox bars for 2.39:1', () => {
  assert.equal(letterbox(1280, 800), Math.round((800 - 1280 / 2.39) / 2));
  assert.equal(letterbox(2390, 1000), 0);
  assert.equal(letterbox(360, 740), Math.round((740 - 360 / 2.39) / 2));
});
