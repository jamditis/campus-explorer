import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parsePaths, snap, route, goalsFor, walkMinutes, STEPS, STREET } from '../viewer/route-math.js';

const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg}: ${a} vs ${b}`);

// A square block, 100 m a side, with stairs as a short cut across the middle:
//   0 (0,0) --- 1 (100,0)
//   |            |
//   3 (0,100) - 2 (100,100)      steps: 0 -> 2 (141 m)
const block = parsePaths({
  nodes: [0, 0, 100, 0, 100, 100, 0, 100],
  edges: [[0, 1, 0, 0], [1, 2, 0, 0], [2, 3, 0, 0], [3, 0, 0, 0], [0, 2, STEPS, 0]],
  entrances: [{ osm: 'way/1', node: 2, mapped: false }],
});
const target = { osm: 'way/1', name: 'Hall', x: 110, z: 110, r: 5 };

test('stairs are the short cut unless step-free', () => {
  const r = route(block, { x: 0, z: -5 }, target);
  near(r.length, Math.hypot(100, 100), 1e-9, 'diagonal');
  assert.equal(r.steps, true);
  const f = route(block, { x: 0, z: -5 }, target, { stepFree: true });
  near(f.length, 200, 1e-9, 'round the block');
  assert.equal(f.steps, false);
  assert.deepEqual(f.points.at(-1), [100, 100]);
});

test('the start snaps onto the nearest edge part way along', () => {
  const s = snap(block, 50, -3);
  assert.equal(s.edge, 0); near(s.t, 0.5, 1e-9, 't'); near(s.distance, 3, 1e-9, 'distance');
  const r = route(block, { x: 50, z: -3 }, target, { stepFree: true });
  near(r.length, 150, 1e-9, 'half the top edge, then down the side');
  assert.deepEqual(r.points[0], [50, 0]);
  near(r.offPath, 3, 1e-9, 'off path');
});

test('no route far from every path or with no way in', () => {
  assert.equal(route(block, { x: 1000, z: 1000 }, target), null);
  const island = parsePaths({ nodes: [0, 0, 10, 0, 500, 0, 510, 0], edges: [[0, 1, 0, 0], [2, 3, 0, 0]], entrances: [{ osm: 'way/9', node: 3 }] });
  assert.equal(route(island, { x: 0, z: 0 }, { osm: 'way/9', x: 510, z: 0 }), null);
});

test('streets cost more than footways of the same length', () => {
  const g = parsePaths({
    nodes: [0, 0, 100, 0, 50, 10],
    edges: [[0, 1, STREET, 0], [0, 2, 0, 0], [2, 1, 0, 0]],
    entrances: [{ osm: 'way/2', node: 1 }],
  });
  // street 100 m costs 125; the footway detour is 2 * hypot(50, 10) = 102 m
  const r = route(g, { x: 0, z: 0 }, { osm: 'way/2', x: 100, z: 0 });
  near(r.length, 2 * Math.hypot(50, 10), 1e-9, 'footway'); near(r.street, 0, 1e-9, 'no street');
});

test('a place without entrances routes to the nearest path', () => {
  const goals = goalsFor(block, { osm: 'node/5', x: 95, z: 45, r: 0 });
  assert.equal(goals.length, 1); assert.equal(goals[0].mapped, false);
});

test('walking minutes', () => {
  assert.equal(walkMinutes(10), 1);
  assert.equal(walkMinutes(780), 10);
});

test('the published paths reach every building in places.json but one, Student Center to CCOM', () => {
  const g = parsePaths(JSON.parse(readFileSync(new URL('../viewer/paths.json', import.meta.url))));
  const places = JSON.parse(readFileSync(new URL('../viewer/places.json', import.meta.url))).places;
  const sc = places.find(p => p.name === 'Student Center'), ccom = places.find(p => p.name === 'College of Communication and Media');
  const r = route(g, { x: sc.x, z: sc.z + sc.r }, ccom);
  assert.ok(r, 'a route');
  // never shorter than the straight line between the two outlines
  assert.ok(r.length >= Math.hypot(sc.x - ccom.x, sc.z - ccom.z) - sc.r - ccom.r);
  const unrouted = places.filter(p => p.kind === 'building' && !route(g, { x: sc.x, z: sc.z + sc.r }, p));
  assert.ok(unrouted.length <= 1, unrouted.map(p => p.name).join(', '));
});
