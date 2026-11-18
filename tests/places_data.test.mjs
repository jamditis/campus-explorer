import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { latLonToLocal } from '../viewer/geo.js';

const root = new URL('../', import.meta.url);
const data = JSON.parse(readFileSync(new URL('viewer/places.json', root), 'utf8'));
const KINDS = new Set(['building', 'parking', 'sports', 'station', 'landmark']);
const TAG_KEYS = new Set(['building', 'building:levels', 'height', 'amenity', 'leisure',
  'railway', 'tourism', 'historic', 'sport', 'operator', 'start_date', 'alt_name',
  'short_name', 'wikidata']);
const TILE_HALF = 80;

function tileCentres(scene) {
  const manifest = JSON.parse(readFileSync(new URL(`models/${scene}/manifest.json`, root), 'utf8'));
  return manifest.tiles.filter((t) => t.center).map((t) => t.center);
}

const CENTRES = { main: tileCentres('main'), north: tileCentres('north') };

test('header', () => {
  assert.equal(data.source, 'OpenStreetMap contributors');
  assert.equal(data.licence, 'ODbL 1.0');
  assert.match(data.fetched, /^\d{4}-\d{2}-\d{2}$/);
  assert.equal(typeof data.frame, 'string');
  assert.ok(Array.isArray(data.places) && data.places.length > 0);
});

test('every place has the expected shape', () => {
  for (const p of data.places) {
    const where = `${p.osm} ${p.name}`;
    assert.equal(typeof p.name, 'string', where);
    assert.ok(p.name.trim().length > 0, where);
    assert.ok(KINDS.has(p.kind), `${where}: kind ${p.kind}`);
    for (const k of ['x', 'z', 'lat', 'lon', 'r']) {
      assert.ok(Number.isFinite(p[k]), `${where}: ${k}`);
    }
    assert.ok(p.r >= 0, where);
    assert.match(p.osm, /^(node|way|relation)\/\d+$/, where);
    if (p.osm.startsWith('node/')) assert.equal(p.r, 0, where);
    assert.ok(Array.isArray(p.scenes) && p.scenes.length > 0, where);
    for (const s of p.scenes) assert.ok(s in CENTRES, `${where}: scene ${s}`);
    assert.equal(typeof p.tags, 'object', where);
    for (const [k, v] of Object.entries(p.tags)) {
      assert.ok(TAG_KEYS.has(k), `${where}: tag ${k}`);
      assert.equal(typeof v, 'string', where);
    }
  }
});

test('osm ids are unique', () => {
  const ids = data.places.map((p) => p.osm);
  assert.equal(new Set(ids).size, ids.length);
});

test('sorted by name, then osm type and id', () => {
  const key = (p) => {
    const [type, id] = p.osm.split('/');
    return [p.name, type, Number(id)];
  };
  const cmp = (a, b) => {
    for (let i = 0; i < a.length; i++) {
      if (a[i] < b[i]) return -1;
      if (a[i] > b[i]) return 1;
    }
    return 0;
  };
  for (let i = 1; i < data.places.length; i++) {
    const a = data.places[i - 1];
    const b = data.places[i];
    assert.ok(cmp(key(a), key(b)) < 0, `${a.name} (${a.osm}) before ${b.name} (${b.osm})`);
  }
});

test('every place lies inside a tile square of each scene it lists', () => {
  for (const p of data.places) {
    for (const scene of Object.keys(CENTRES)) {
      const inside = CENTRES[scene].some(([cx, cz]) =>
        Math.abs(p.x - cx) <= TILE_HALF && Math.abs(p.z - cz) <= TILE_HALF);
      assert.equal(p.scenes.includes(scene), inside, `${p.osm} ${p.name} in ${scene}`);
    }
  }
});

test('lat/lon round-trips through viewer/geo.js to x/z within 0.05 m', () => {
  for (const p of data.places) {
    const { x, z } = latLonToLocal(p.lat, p.lon);
    assert.ok(Math.abs(x - p.x) <= 0.05 && Math.abs(z - p.z) <= 0.05,
      `${p.osm} ${p.name}: (${x}, ${z}) vs (${p.x}, ${p.z})`);
  }
});
