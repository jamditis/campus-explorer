import test from 'node:test';
import assert from 'node:assert/strict';
import {
  labelPriority, distanceOpacity, inRange, declutter, selectStops, tourCaption, sourceTitle, southWestOffset, TOUR_NAMES,
} from '../viewer/labels-math.js';

test('priority ranks kind, then size, then nearness', () => {
  assert.ok(labelPriority('building', 20, 300) > labelPriority('sports', 20, 300));
  assert.ok(labelPriority('sports', 20, 300) > labelPriority('parking', 20, 300));
  assert.equal(labelPriority('station', 20, 300), labelPriority('building', 20, 300));
  assert.ok(labelPriority('building', 50, 300) > labelPriority('building', 10, 300));
  assert.ok(labelPriority('building', 20, 100) > labelPriority('building', 20, 900));
  assert.ok(Number.isFinite(labelPriority('unknown', NaN, 0)));
});

test('distance opacity fades between near and far', () => {
  assert.equal(distanceOpacity(10), 1);
  assert.equal(distanceOpacity(800), 1);
  assert.ok(Math.abs(distanceOpacity(1100) - 0.5) < 1e-9);
  assert.equal(distanceOpacity(1400), 0);
  assert.equal(distanceOpacity(NaN), 0);
});

test('parking shows only close up; minimum hides near labels', () => {
  assert.equal(inRange('parking', 300), true);
  assert.equal(inRange('parking', 400), false);
  assert.equal(inRange('building', 1300), true);
  assert.equal(inRange('building', 1500), false);
  assert.equal(inRange('building', 10, { minimum: 12 }), false);
  assert.equal(inRange('building', 13, { minimum: 12 }), true);
});

test('declutter keeps the best label of an overlapping pair', () => {
  const items = [
    { x: 0, y: 0, w: 100, h: 20, priority: 1 },
    { x: 50, y: 5, w: 100, h: 20, priority: 5 },
    { x: 300, y: 0, w: 100, h: 20, priority: 2 },
  ];
  assert.deepEqual(declutter(items), [1, 2]);
});

test('declutter shows forced labels and respects max', () => {
  const items = [
    { x: 0, y: 0, w: 100, h: 20, priority: 9 },
    { x: 10, y: 0, w: 100, h: 20, priority: 0, forced: true },
    { x: 400, y: 0, w: 10, h: 10, priority: 3 },
    { x: 600, y: 0, w: 10, h: 10, priority: 2 },
  ];
  assert.deepEqual(declutter(items, { max: 2 }), [1, 2]);
});

test('declutter skips labels under the interface unless forced', () => {
  const items = [
    { x: 0, y: 0, w: 50, h: 20, priority: 5 },
    { x: 100, y: 0, w: 50, h: 20, priority: 1 },
    { x: 10, y: 0, w: 20, h: 20, priority: 0, forced: true },
  ];
  assert.deepEqual(declutter(items, { blocked: [{ x: 0, y: 0, w: 60, h: 60 }] }), [2, 1]);
});

test('declutter result never overlaps', () => {
  const items = Array.from({ length: 200 }, (_, i) => ({
    x: (i * 37) % 900, y: (i * 53) % 600, w: 60 + (i % 5) * 20, h: 22, priority: (i * 7919) % 101,
  }));
  const shown = declutter(items, { pad: 0 });
  for (const a of shown) {
    for (const b of shown) {
      if (a === b) continue;
      const A = items[a], B = items[b];
      assert.ok(!(A.x < B.x + B.w && B.x < A.x + A.w && A.y < B.y + B.h && B.y < A.y + A.h), `${a} overlaps ${b}`);
    }
  }
});

test('selectStops keeps tour order and skips missing names', () => {
  const places = [{ name: 'Life Hall' }, { name: 'Red Hawk Deck' }, { name: 'Somewhere else' }, { name: 'NJ Transit Deck' }];
  assert.deepEqual(selectStops(places).map(p => p.name), ['Red Hawk Deck', 'Life Hall', 'NJ Transit Deck']);
  assert.deepEqual(selectStops(null), []);
  assert.equal(TOUR_NAMES.length, 15);
});

test('tour caption uses only OpenStreetMap facts', () => {
  const c = tourCaption({ name: 'Life Hall', kind: 'building', tags: { start_date: '1908' } }, 2, 15);
  assert.equal(c.title, 'Life Hall');
  assert.equal(c.counter, '3 of 15');
  assert.deepEqual(c.details, ['Building', 'OpenStreetMap start date: 1908']);
  assert.equal(c.source, 'Names from OpenStreetMap');
  assert.deepEqual(tourCaption({ name: 'X', kind: 'parking', tags: {} }, 0, 1).details, ['Parking']);
});

test('source title cites the OSM element', () => {
  assert.equal(sourceTitle({ osm: 'way/123' }), 'Name and position from OpenStreetMap (way/123)');
});

test('south-west offset sits west and south of the target', () => {
  const o = southWestOffset(40);
  assert.ok(o.dx < 0 && o.dz > 0 && o.dy > 0);
  assert.ok(Math.abs(Math.hypot(o.dx, o.dz) - 96 * 0.8) < 1e-9);
});
