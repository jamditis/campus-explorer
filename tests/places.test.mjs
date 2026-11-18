import test from 'node:test';
import assert from 'node:assert/strict';
import { forScene, searchPlaces, nearestPlace, normalize } from '../viewer/places.js';

const place = (name, extra = {}) => ({
  name, kind: 'building', x: 0, z: 0, lat: 0, lon: 0, r: 10, osm: 'way/1', scenes: ['main'], tags: {}, ...extra,
});

const places = [
  place('Susan A. Cole Hall', { tags: { short_name: 'Cole' } }),
  place('College Hall'),
  place('Cole'),
  place('Coleman House'),
  place('Café Diem'),
  place('University Hall', { tags: { alt_name: 'UN Hall;Uni' } }),
  place('Blanton Hall', { scenes: ['north'] }),
  place('Nicholas Center'),
];

const top = (q, list = places) => searchPlaces(list, q).map((h) => h.place.name);

test('normalize folds case, diacritics and punctuation', () => {
  assert.equal(normalize('Café  Diem'), 'cafe diem');
  assert.equal(normalize('Susan A. Cole Hall'), 'susan a cole hall');
  assert.equal(normalize("O'Neil-Smith"), 'oneil smith');
  assert.equal(normalize('  ÅNGSTRÖM ﬁeld '), 'angstrom field');
  assert.equal(normalize(null), '');
});

test('forScene filters by scene', () => {
  assert.deepEqual(forScene(places, 'north').map((p) => p.name), ['Blanton Hall']);
  assert.equal(forScene(places, 'main').length, 7);
  assert.deepEqual(forScene(null, 'main'), []);
  assert.deepEqual(forScene([{ name: 'x' }], 'main'), []);
});

test('empty query returns nothing', () => {
  assert.deepEqual(searchPlaces(places, ''), []);
  assert.deepEqual(searchPlaces(places, '   '), []);
  assert.deepEqual(searchPlaces(places, '...'), []);
  assert.deepEqual(searchPlaces([], 'cole'), []);
});

test('ranking: exact > prefix > word prefix > alt name', () => {
  // Cole: exact. Coleman House: starts with. Susan A. Cole Hall: word starts with.
  // College Hall and Nicholas Center only match as subsequences (c-o-l-e).
  assert.deepEqual(top('cole'), ['Cole', 'Coleman House', 'Susan A. Cole Hall', 'College Hall', 'Nicholas Center']);
  const scores = searchPlaces(places, 'cole').map((h) => h.score);
  assert.deepEqual([...scores].sort((a, b) => b - a), scores);
  assert.equal(new Set(scores.slice(0, 4)).size, 4);
});

test('every query word as a word prefix, any order', () => {
  assert.equal(top('hall cole')[0], 'Susan A. Cole Hall');
  assert.equal(top('cole hall')[0], 'Susan A. Cole Hall');
});

test('substring below word matches', () => {
  // "olem" is inside Coleman but not at a word start.
  const hits = searchPlaces(places, 'olem');
  assert.equal(hits[0].place.name, 'Coleman House');
  assert.ok(hits[0].score < searchPlaces(places, 'coleman')[0].score);
});

test('diacritics insensitive both ways', () => {
  assert.equal(top('cafe')[0], 'Café Diem');
  assert.equal(top('CAFÉ DIEM')[0], 'Café Diem');
});

test('alt_name and short_name rank just below name matches', () => {
  assert.equal(top('uni')[0], 'University Hall');
  const altOnly = [place('Main Building', { tags: { alt_name: 'Old Hall;UN Hall' } })];
  const un = searchPlaces(altOnly, 'un hall');
  assert.equal(un[0].place.name, 'Main Building');
  const nameHit = searchPlaces([place('UN Hall Annex')], 'un hall')[0].score;
  // A name prefix outranks an exact alt name.
  assert.ok(nameHit > un[0].score);
  // A substring name match still beats any alt match.
  const sub = searchPlaces([place('Xun hallway')], 'un hall')[0].score;
  assert.ok(sub > un[0].score);
});

test('subsequence is typo tolerant only for 3+ characters', () => {
  assert.equal(top('nchls')[0], 'Nicholas Center');
  assert.deepEqual(top('nc'), []);
  assert.deepEqual(top('zzz'), []);
});

test('ties: shorter name, then alphabetical', () => {
  const list = [place('Hall Beta'), place('Hall Zed'), place('Hall Alpha'), place('Hall Abc'), place('Hall B')];
  assert.deepEqual(top('hall', list), ['Hall B', 'Hall Abc', 'Hall Zed', 'Hall Beta', 'Hall Alpha']);
});

test('limit', () => {
  const list = Array.from({ length: 20 }, (_, i) => place(`Lot ${i}`));
  assert.equal(searchPlaces(list, 'lot').length, 8);
  assert.equal(searchPlaces(list, 'lot', 3).length, 3);
  assert.equal(searchPlaces(list, 'lot', 0).length, 0);
});

test('skips places without a name', () => {
  assert.deepEqual(top('hall', [{ kind: 'x' }, null, place('Hall')]), ['Hall']);
});

test('nearestPlace measures to the footprint circle', () => {
  const list = [place('A', { x: 0, z: 0, r: 50 }), place('B', { x: 30, z: 0, r: 0 })];
  // At (60, 0): A is 60 - 50 = 10 away, B is 30 away.
  assert.deepEqual(nearestPlace(list, 60, 0), { place: list[0], distance: 10 });
  assert.equal(nearestPlace(list, 10, 0).distance, 0);
  assert.equal(nearestPlace(list, 1000, 0, 100), null);
  assert.equal(nearestPlace(list, 150, 0, 100).distance, 100);
});

test('nearestPlace handles empty and bad input', () => {
  assert.equal(nearestPlace([], 0, 0), null);
  assert.equal(nearestPlace(null, 0, 0), null);
  assert.equal(nearestPlace([place('A')], NaN, 0), null);
  const list = [place('Bad', { x: NaN }), place('NoR', { x: 5, z: 0, r: undefined })];
  assert.deepEqual(nearestPlace(list, 0, 0), { place: list[1], distance: 5 });
});
