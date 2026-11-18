import test from 'node:test';
import assert from 'node:assert/strict';
import { VALUE, GROUPS, shows, hidden, glslTest } from '../viewer/ownership.js';

test('each model shows exactly the cells it should', () => {
  const expected = {
    //            none  northEdge north  mainEdge main
    main: [true, false, false, true, true],
    north: [true, true, true, true, false],
    skirt: [true, true, false, true, true],
  };
  const values = [VALUE.none, VALUE.northEdge, VALUE.north, VALUE.mainEdge, VALUE.main];
  for (const group of GROUPS) assert.deepEqual(values.map(v => shows(group, v)), expected[group], group);
});

test('every interior cell is drawn by exactly one terrain, border cells by two', () => {
  const drawn = v => ['main', 'north', 'skirt'].filter(g => shows(g, v));
  assert.deepEqual(drawn(VALUE.main), ['main', 'skirt']); // the skirt is cut out under the main campus in Blender
  assert.deepEqual(drawn(VALUE.north), ['north']);
  assert.deepEqual(drawn(VALUE.northEdge), ['north', 'skirt']);
  assert.deepEqual(drawn(VALUE.mainEdge), ['main', 'north', 'skirt']);
});

test('a grey level shifted by one on decode changes nothing', () => {
  for (const v of Object.values(VALUE)) for (const group of GROUPS) for (const d of [-1, 1]) {
    const w = Math.min(255, Math.max(0, v + d));
    assert.equal(shows(group, w), shows(group, v), `${group} at ${v}${d > 0 ? '+1' : '-1'}`);
  }
});

test('the shader test is the same predicate', () => {
  for (const group of GROUPS) {
    const fn = new Function('o', `return ${glslTest(group)};`);
    for (let v = 0; v <= 255; v++) assert.equal(fn(v / 255), hidden(group, v / 255), `${group} ${v}`);
  }
});

test('an unknown group hides nothing', () => {
  assert.equal(shows('avatar', VALUE.north), true);
});
