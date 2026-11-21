import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BufferAttribute, Quaternion, Matrix4, Vector3 } from '../vendor/three.module.js';
import { toNormalizedInt16, farImageSize, linearPart, instanceShift, unitQuats, fewestBits, decodeUnit, isWhite } from '../tools/web-export/pack.mjs';

test('instance rotations stored as normalized int16 decode to the same turn in three.js', () => {
  const qs = [[0, 0, 0, 1], [0, 0.3826834, 0, 0.9238795], [0.1, -0.7, 0.2, 0.6782330], [0, -1, 0, 0]];
  const packed = toNormalizedInt16(new Float32Array(qs.flat()));
  assert.ok(packed instanceof Int16Array);
  assert.equal(packed[3], 32767);
  assert.equal(packed[13], -32767);
  // the path GLTFLoader takes for EXT_mesh_gpu_instancing: a normalized attribute read per instance
  const attr = new BufferAttribute(packed, 4, true), q = new Quaternion();
  qs.forEach((want, i) => {
    q.fromBufferAttribute(attr, i);
    const dot = Math.abs(q.x * want[0] + q.y * want[1] + q.z * want[2] + q.w * want[3]);
    const angle = 2 * Math.acos(Math.min(1, dot));
    assert.ok(angle < 1e-4, `instance ${i} turned by ${angle} rad`);
  });
});

test('values outside -1..1 are clamped, not wrapped', () => {
  assert.deepEqual([...toNormalizedInt16(new Float32Array([1.00001, -1.2]))], [32767, -32767]);
});

test('far-version images are half size per side, never below one pixel', () => {
  assert.deepEqual(farImageSize([1024, 1024]), [512, 512]);
  assert.deepEqual(farImageSize([1781, 1685]), [891, 843]);
  assert.deepEqual(farImageSize([200, 1]), [100, 1]);
  assert.deepEqual(farImageSize([64, 64]), [64, 64]); // small images are left as they are
});

test('the linear part of an instance matrix is what three.js composes, unit quaternion or not', () => {
  for (const [q, sc] of [[[0, 0, 0, 1], [1, 1, 1]], [[0.1, -0.7, 0.2, 0.678233], [2, 0.5, 3]], [[0.3, 0.2, -0.1, 0.9], [1.5, 1.5, 1.5]]]) {
    const m = new Matrix4().compose(new Vector3(), new Quaternion(...q), new Vector3(...sc)).elements;
    const want = [m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]];
    linearPart(q, sc).forEach((v, i) => assert.ok(Math.abs(v - want[i]) < 1e-12, `${q} ${i}`));
  }
});

test('an instance shift bounds how far any vertex within the radius moves', () => {
  const a = { t: [1, 2, 3], q: [0, 0, 0, 1], s: [1, 1, 1] };
  assert.equal(instanceShift(a, a, 10), 0);
  assert.ok(Math.abs(instanceShift(a, { ...a, t: [1.003, 2, 3] }, 10) - 0.003) < 1e-12);
  // a 1 mrad turn moves a vertex 5 m out by 5 mm; the bound may be larger, never smaller
  const turned = { ...a, q: [0, Math.sin(0.0005), 0, Math.cos(0.0005)] };
  const shift = instanceShift(a, turned, 5);
  assert.ok(shift >= 0.005 - 1e-9 && shift < 0.0075, `${shift}`);
  // scale: 1 % larger, 2 m radius: at least 2 cm
  assert.ok(instanceShift(a, { ...a, s: [1.01, 1.01, 1.01] }, 2) >= 0.02 - 1e-9);
  // a quaternion a little off unit length composes to a slightly sheared matrix: making it unit moves vertices
  const off = { ...a, q: [0, 0.3 * 0.99, 0, 0.9539392 * 0.99] }, unit = { ...off, q: unitQuats(new Float32Array(off.q)) };
  assert.ok(instanceShift(off, unit, 1) > 0.005);
});

test('quaternions are made unit length, and decoded from normalized integers', () => {
  const u = unitQuats(new Float32Array([0, 0, 0, 2, 0, 3, 0, 4, 0, 0, 0, 0]));
  assert.deepEqual([...u.slice(0, 8)].map(x => +x.toFixed(6)), [0, 0, 0, 1, 0, 0.6, 0, 0.8]);
  assert.deepEqual([...u.slice(8)], [0, 0, 0, 1]); // a zero quaternion becomes no turn
  assert.deepEqual([...decodeUnit(new Int16Array([32767, -32767, -32768, 0]))], [1, -1, -1, 0]);
  assert.deepEqual([...decodeUnit(new Int8Array([127, -128]))], [1, -1]);
  assert.deepEqual([...decodeUnit(new Uint8Array([255, 0]))], [1, 0]);
});

test('fewestBits takes the first candidate within tolerance, else null', () => {
  const err = b => 2 ** -b;
  assert.equal(fewestBits([8, 10, 12, 14], err, 0.001), 10);
  assert.equal(fewestBits([8, 10], err, 1e-6), null);
});

test('a vertex colour is dropped only when every vertex is opaque white, which multiplies by one', () => {
  assert.equal(isWhite(new Uint8Array([255, 255, 255, 255, 255, 255, 255, 255]), true), true);
  assert.equal(isWhite(new Uint16Array([65535, 65535, 65535]), true), true);
  assert.equal(isWhite(new Float32Array([1, 1, 1, 1]), false), true);
  assert.equal(isWhite(new Uint8Array([255, 255, 254, 255]), true), false);
  assert.equal(isWhite(new Uint8Array([255, 255, 255, 128]), true), false); // see-through
  assert.equal(isWhite(new Float32Array([1, 0.99, 1]), false), false);
  assert.equal(isWhite(new Uint8Array([]), true), false);
});
