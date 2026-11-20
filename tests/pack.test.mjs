import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BufferAttribute, Quaternion } from '../vendor/three.module.js';
import { toNormalizedInt16, farImageSize } from '../tools/web-export/pack.mjs';

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
