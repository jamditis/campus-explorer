import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  parseRooms, inRing, ringGap, inVolume, volumeGap, nearVolumes, volumeAt, floorAt, visibleRooms,
  roomPlaces, searchPool, walkStartY, INTERIOR_REACH, interiorLit, ambientFactor, roomHere, sightPass,
} from '../viewer/rooms-math.js';

// a 20 x 10 m building in viewer metres, floors at 100 and 104, roof at 110
const DATA = {
  volumes: [{
    id: 't', building: 'Test Hall', short: 'TH', ring: [[0, 0], [20, 0], [20, -10], [0, -10]],
    y0: 100, y1: 110, levels: [{ floor: 2, y: 104 }, { floor: 1, y: 100 }],
  }],
  rooms: [
    { name: '1001', x: 5, z: -5, y: 100, floor: 1, building: 'Test Hall', unverified: true },
    { name: '2001', x: 5, z: -5, y: 104, floor: 2, building: 'Test Hall', unverified: true },
    { name: '2002', x: 18, z: -5, y: 104, floor: 2, building: 'Test Hall', unverified: true },
  ],
};
const D = parseRooms(DATA), V = D.volumes[0];

test('parse keeps good volumes and rooms, sorts levels, drops broken entries', () => {
  assert.deepEqual(V.levels.map(l => l.floor), [1, 2]);
  assert.equal(D.rooms.length, 3);
  const bad = parseRooms({ volumes: [{ ring: [[0, 0]], y0: 1, y1: 2 }, null], rooms: [{ name: 'x' }, 5] });
  assert.deepEqual(bad, { volumes: [], rooms: [] });
  assert.deepEqual(parseRooms(null), { volumes: [], rooms: [] });
});

test('ring tests: inside, outside, gap to the nearest edge', () => {
  assert.equal(inRing(V.ring, 5, -5), true);
  assert.equal(inRing(V.ring, 25, -5), false);
  assert.equal(ringGap(V.ring, 5, -5), 0);
  assert.equal(ringGap(V.ring, 25, -5), 5);
  assert.ok(Math.abs(ringGap(V.ring, 23, 4) - 5) < 1e-9); // off a corner
});

test('a volume grown by a metre takes glass on the wall line and just outside it', () => {
  assert.equal(inVolume(V, 20.5, 105, -5), false);
  assert.equal(inVolume(V, 20.5, 105, -5, 1), true);
  assert.equal(inVolume(V, 21.5, 105, -5, 1), false);
  assert.equal(inVolume(V, 5, 110.8, -5, 1), true);
  assert.equal(inVolume(V, 5, 111.2, -5, 1), false);
  assert.equal(inVolume(V, 5, 99.5, -5, 1), true);
});

test('the interior rule works within reach of a volume, inside or out', () => {
  assert.equal(volumeGap(V, 5, 105, -5), 0);
  assert.equal(volumeGap(V, 50, 105, -5), 30);
  assert.equal(volumeGap(V, 5, 140, -5), 30); // straight above the roof
  assert.ok(Math.abs(volumeGap(V, 50, 150, -5) - 50) < 1e-9);
  assert.equal(INTERIOR_REACH, 40);
  assert.deepEqual(nearVolumes(D.volumes, { x: 50, y: 105, z: -5 }), [0]);
  assert.deepEqual(nearVolumes(D.volumes, { x: 70, y: 105, z: -5 }), []);
  assert.equal(volumeAt(D.volumes, { x: 5, y: 105, z: -5 }), 0);
  assert.equal(volumeAt(D.volumes, { x: 50, y: 105, z: -5 }), -1);
});

test('the floor comes from the camera height against the levels', () => {
  assert.equal(floorAt(V.levels, 101.65), 1);
  assert.equal(floorAt(V.levels, 104.2), 1); // still on the stair below floor 2
  assert.equal(floorAt(V.levels, 105.65), 2);
  assert.equal(floorAt(V.levels, 99), 1);
  assert.equal(floorAt([], 99), null);
});

test('room labels show for the floor you are on, near, in walk mode or inside', () => {
  const at = (x, y, z) => ({ x, y, z });
  // inside on floor 2, orbit: both floor 2 rooms within 20 m
  assert.deepEqual(visibleRooms(D, at(6, 105.65, -5), 'orbit'), [1, 2]);
  // inside on floor 1
  assert.deepEqual(visibleRooms(D, at(6, 101.65, -5), 'fly'), [0]);
  // outside, orbit: none; outside in walk mode within 20 m of the room: shown
  assert.deepEqual(visibleRooms(D, at(-10, 101.65, -5), 'orbit'), []);
  assert.deepEqual(visibleRooms(D, at(-10, 101.65, -5), 'walk'), [0]);
  assert.deepEqual(visibleRooms(D, at(-30, 101.65, -5), 'walk'), []);
  assert.deepEqual(visibleRooms(D, at(6, 105.65, -5), 'orbit', { reach: 5 }), [1]);
});

test('rooms become search places named by the short name, flown to at their floor', () => {
  const p = roomPlaces(D);
  assert.equal(p.length, 3);
  assert.equal(p[0].name, 'TH 1001');
  assert.equal(p[0].kind, 'room');
  assert.equal(p[0].y, 100);
  assert.match(p[0].tags.alt_name, /Room 1001/);
  const long = roomPlaces(parseRooms({ ...DATA, volumes: [{ ...DATA.volumes[0], short: '' }] }));
  assert.equal(long[0].name, 'Test Hall 1001');
});

test('rooms join the search only for a query with a digit', () => {
  const places = [{ name: 'Test Hall' }], rooms = roomPlaces(D);
  assert.equal(searchPool(places, rooms, 'test').length, 1);
  assert.equal(searchPool(places, rooms, 'TH 2001').length, 4);
  assert.equal(searchPool(places, rooms, '2001').length, 4);
});

test('walk starts on the storey the camera is on, from orbit and from fly', () => {
  assert.equal(walkStartY('orbit', 141.2), 141.2);
  assert.equal(walkStartY('fly', 143.5), 143.5);
  assert.equal(walkStartY('walk', 143.5), null);
  assert.equal(walkStartY('fly', NaN), null);
});

test('the published rooms file parses, and every room lies in its volume', () => {
  const data = parseRooms(JSON.parse(readFileSync(new URL('../viewer/rooms.json', import.meta.url))));
  assert.ok(data.volumes.length >= 1 && data.rooms.length >= 1);
  for (const r of data.rooms) {
    const v = data.volumes.find(x => x.building === r.building);
    assert.ok(v && inRing(v.ring, r.x, r.z), r.name);
  }
});

test('interior light: inside the ring, away from the outer wall face, not on the roof', () => {
  const v = { ...V, ceiling: 107 };
  assert.equal(interiorLit(v, 5, 101, -5, 0), true); // an inner wall
  assert.equal(interiorLit(v, 5, 106.9, -5, -1), true); // the top floor's ceiling
  assert.equal(interiorLit(v, 5, 100.0, -5, 1), true); // a floor
  assert.equal(interiorLit(v, 20, 101, -5, 0), false); // the outer face of the shell, on the outline
  assert.equal(interiorLit(v, 19.9, 101, -5, 0), false); // within EDGE of it
  assert.equal(interiorLit(v, 19.6, 101, -5, 0), true); // the inner face of a 0.4 m wall
  assert.equal(interiorLit(v, 5, 109.5, -5, 1), false); // the roof, facing up, above the ceiling
  assert.equal(interiorLit(v, 5, 109.5, -5, -1), true); // under the roof (an atrium), facing down
  assert.equal(interiorLit(v, 5, 109.7, -5, 0), false); // a parapet in the top half metre
  assert.equal(interiorLit(v, 5, 109.7, -5, -1), true); // the underside of a flat roof with no ceiling under it
  assert.equal(interiorLit(v, 25, 101, -5, 0), false); // outside
  assert.equal(interiorLit(v, 5, 111, -5, -1), false); // above the volume
});

test('interior light is strongest on ceilings and weakest on floors', () => {
  assert.ok(ambientFactor(-1) > ambientFactor(0) && ambientFactor(0) > ambientFactor(1));
  assert.equal(ambientFactor(-1), 1);
});

test('the room you stand in is the nearest room point on your floor, inside the building', () => {
  assert.equal(roomHere(D, { x: 6, y: 105.65, z: -5 }), 1);
  assert.equal(roomHere(D, { x: 17, y: 105.65, z: -5 }), 2);
  assert.equal(roomHere(D, { x: 6, y: 101.65, z: -5 }), 0);
  assert.equal(roomHere(D, { x: 12, y: 105.65, z: -5 }), -1); // more than ROOM_HERE from any room point
  assert.equal(roomHere(D, { x: -3, y: 101.65, z: -5 }), -1); // outside
});

test('line of sight: a dozen rays a pass, unchecked rooms first, the room you are in always shows', () => {
  const ids = Array.from({ length: 30 }, (_, i) => i);
  const memo = new Map(); let rays = 0;
  const clear = id => { rays++; return id % 2 === 0; }; // odd rooms are behind walls
  let shown = sightPass(ids, memo, clear, { budget: 12, here: 7 });
  assert.equal(rays, 12);
  assert.deepEqual([...shown].sort((a, b) => a - b), [0, 2, 4, 6, 7, 8, 10, 12]); // no ray for the room you are in
  sightPass(ids, memo, clear, { budget: 12, here: 7 });
  shown = sightPass(ids, memo, clear, { budget: 12, here: 7 });
  assert.equal(rays, 36); // every room checked once, the next pass starts again with the oldest
  assert.equal(shown.size, 16); // 15 even rooms and the room you stand in
  assert.equal(sightPass([], memo, clear).size, 0);
});
