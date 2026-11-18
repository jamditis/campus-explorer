import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  TARGET_NAMES, STATUE, REACH, selectTargets, isFound, nearestTarget, arrowAngle,
  horizontalDistance, formatElapsed, parseProgress,
} from '../viewer/hunt-math.js';
import { CAMPUS, convergenceDeg } from '../viewer/geo.js';

const places = JSON.parse(readFileSync(new URL('../viewer/places.json', import.meta.url))).places;
const near = (a, b, tol = 1e-9, msg = '') => assert.ok(Math.abs(a - b) <= tol, `${msg} ${a} vs ${b}`);

test('every target name is in places.json', () => {
  const names = new Set(places.map(p => p.name));
  for (const n of TARGET_NAMES) assert.ok(names.has(n), n);
});

test('targets: named places in order, then the statue', () => {
  const t = selectTargets(places);
  assert.equal(t.length, 9);
  assert.deepEqual(t.slice(0, 8).map(p => p.name), [...TARGET_NAMES]);
  assert.equal(t[8].name, STATUE.name);
  assert.equal(t[1].label, 'Kasser Theater');
});

test('missing places are skipped', () => {
  const t = selectTargets(places.filter(p => p.name !== 'Sprague Library'));
  assert.equal(t.length, 8);
  assert.ok(!t.some(p => p.name === 'Sprague Library'));
  assert.deepEqual(selectTargets([]).map(p => p.name), [STATUE.name]);
});

test('found within r + REACH, horizontally', () => {
  const t = { name: 'x', x: 0, z: 0, r: 10 };
  assert.equal(isFound(t, { x: 10 + REACH, y: 999, z: 0 }), true);
  assert.equal(isFound(t, { x: 0, z: 10 + REACH + 0.01 }), false);
  assert.equal(isFound({ x: 0, z: 0 }, { x: REACH, z: 0 }), true, 'missing r counts as 0');
});

test('nearest unfound target', () => {
  const targets = [{ name: 'a', x: 0, z: 0 }, { name: 'b', x: 100, z: 0 }, { name: 'c', x: 0, z: 30 }];
  const pos = { x: 0, z: 10 };
  assert.equal(nearestTarget(targets, [], pos).target.name, 'a');
  const r = nearestTarget(targets, new Set(['a']), pos);
  assert.equal(r.target.name, 'c'); near(r.distance, 20);
  assert.equal(nearestTarget(targets, ['a', 'b', 'c'], pos), null);
  near(horizontalDistance({ x: 0, z: 0 }, { x: 3, z: 4 }), 5);
});

test('arrow angle is relative to the view', () => {
  const conv = convergenceDeg(CAMPUS.lat, CAMPUS.lon);
  const o = { x: 0, z: 0 };
  const north = { x: 0, z: -50 }, east = { x: 50, z: 0 };
  near(arrowAngle(o, north, conv), 0, 1e-9, 'looking at grid north, target ahead');
  near(arrowAngle(o, east, conv), 90, 1e-9, 'target to the right');
  near(arrowAngle(o, north, conv + 90), -90, 1e-9, 'looking east, north is to the left');
  near(arrowAngle(o, { x: 0, z: 50 }, conv), 180, 1e-9, 'behind');
  const a = arrowAngle(o, east, 350);
  assert.ok(a > -180 && a <= 180);
});

test('elapsed time', () => {
  assert.equal(formatElapsed(45_000), '45 s');
  assert.equal(formatElapsed(252_000), '4 min 12 s');
  assert.equal(formatElapsed(3_780_000), '1 h 3 min');
});

test('saved progress', () => {
  assert.deepEqual(parseProgress('{"found":["Amphitheater",3],"start":5}'), { found: ['Amphitheater'], start: 5, end: null });
  assert.deepEqual(parseProgress('nope'), { found: [], start: null, end: null });
  assert.deepEqual(parseProgress(null), { found: [], start: null, end: null });
});
