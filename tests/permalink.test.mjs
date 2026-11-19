import test from 'node:test';
import assert from 'node:assert/strict';
import { encodeView, decodeView } from '../viewer/permalink.js';

const view = {
  scene: 'main',
  mode: 'orbit',
  position: [181.94, 350.8, 410.6],
  target: [-45, 120, 60],
  time: '2026-09-22T14:40',
  labels: true,
};

test('encodes in fixed order with 0.1 m rounding', () => {
  assert.equal(
    encodeView(view),
    'v=1&s=main&m=orbit&c=181.9,350.8,410.6&t=-45.0,120.0,60.0&d=2026-09-22T14:40&l=1',
  );
});

test('omits time when null and labels when off', () => {
  assert.equal(
    encodeView({ ...view, time: null, labels: false }),
    'v=1&s=main&m=orbit&c=181.9,350.8,410.6&t=-45.0,120.0,60.0',
  );
});

test('never writes -0.0', () => {
  assert.equal(encodeView({ position: [-0.01, 0, -0.04] }), 'v=1&c=0.0,0.0,0.0');
});

test('encode skips invalid fields', () => {
  assert.equal(encodeView({ scene: 'moon', mode: 'swim', position: [NaN, 0, 0], time: 'later' }), 'v=1');
  assert.equal(encodeView(null), 'v=1');
});

test('decodes with or without #', () => {
  const s = encodeView(view);
  const expected = { ...view, position: [181.9, 350.8, 410.6], target: [-45, 120, 60] };
  assert.deepEqual(decodeView(s), expected);
  assert.deepEqual(decodeView(`#${s}`), expected);
});

test('round trip is stable', () => {
  const samples = [
    encodeView(view),
    'v=1&s=north&m=walk&c=1.0,2.0,3.0',
    'v=1&m=fly&d=2024-02-29T00:00',
    'v=1&t=-19999.9,0.0,19999.9&l=1',
  ];
  for (const s of samples) {
    assert.equal(encodeView(decodeView(s)), s);
    assert.equal(encodeView(decodeView(encodeView(decodeView(s)))), s);
  }
});

test('accepts percent-encoded commas and colons', () => {
  const v = decodeView('c=1%2C2%2C3&d=2026-01-01T09%3A05');
  assert.deepEqual(v.position, [1, 2, 3]);
  assert.equal(v.time, '2026-01-01T09:05');
});

test('returns null for garbage', () => {
  for (const h of ['', '#', 'hello', '#%%%', '&&&', 'v=1', 'v=99', 'x=1&y=2', 's=moon', 'c=a,b,c', 'l=yes']) {
    assert.equal(decodeView(h), null, h);
  }
  for (const h of [null, undefined, 42, {}, []]) assert.equal(decodeView(h), null);
});

test('unknown scene or mode is undefined, other fields survive', () => {
  const v = decodeView('s=moon&m=swim&c=1,2,3');
  assert.equal(v.scene, undefined);
  assert.equal(v.mode, undefined);
  assert.deepEqual(v.position, [1, 2, 3]);
});

test('rejects bad coordinates', () => {
  const bad = [
    'NaN,0,0', 'Infinity,0,0', '1,2', '1,2,3,4', '1,,3', ',,', '0x10,0,0',
    '20000.1,0,0', '0,-20001,0', '1e9,0,0', '1e400,0,0', '1 2 3', 'abc',
  ];
  for (const c of bad) {
    const v = decodeView(`c=${encodeURIComponent(c)}&s=main`);
    assert.equal(v.position, undefined, c);
    assert.equal(v.scene, 'main');
  }
});

test('accepts coordinates at the limit and rounds them', () => {
  const v = decodeView('c=20000,-20000,1.26&t=1e2,0,-.5');
  assert.deepEqual(v.position, [20000, -20000, 1.3]);
  assert.deepEqual(v.target, [100, 0, -0.5]);
  for (const n of [...v.position, ...v.target]) assert.ok(Number.isFinite(n));
});

test('rejects impossible dates and times', () => {
  const bad = [
    '2026-02-29T10:00', '2026-13-01T10:00', '2026-00-10T10:00', '2026-04-31T10:00',
    '2026-01-01T24:00', '2026-01-01T10:60', '2026-1-1T1:00', '2026-01-01 10:00',
    '2026-01-01T10:00:00', '0000-01-01T00:00', 'now',
  ];
  for (const d of bad) {
    const v = decodeView(`d=${encodeURIComponent(d)}&m=fly`);
    assert.equal(v.time, undefined, d);
  }
  assert.equal(decodeView('d=2000-02-29T23:59').time, '2000-02-29T23:59');
  assert.equal(decodeView('d=1900-02-29T12:00'), null);
});

test('absent d and l give null time and labels off', () => {
  const v = decodeView('s=north');
  assert.equal(v.time, null);
  assert.equal(v.labels, false);
});

test('ignores unknown keys and decodes known fields of a later version', () => {
  const v = decodeView('v=7&zoom=3&s=north&q=hello&l=1');
  assert.equal(v.scene, 'north');
  assert.equal(v.labels, true);
});

test('never throws on hostile input', () => {
  const inputs = ['%E0%A4%A', '#c=%', 'c=1,2,3&c=4,5,6', '='.repeat(1000), 'c=' + '9'.repeat(400) + ',0,0'];
  for (const h of inputs) assert.doesNotThrow(() => decodeView(h));
});
