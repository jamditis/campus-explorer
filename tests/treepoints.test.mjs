import test from 'node:test';
import assert from 'node:assert/strict';
import { mul, compose, apply, leafKind, treeGroups, record, leafColour, srgbToLinear } from '../tools/web-export/treepoints.mjs';

const near = (a, b, e = 1e-6) => a.every((v, i) => Math.abs(v - b[i]) < e);

test('compose and mul follow glTF: translation, unit quaternion, scale, column-major', () => {
  const q = [0, Math.SQRT1_2, 0, Math.SQRT1_2]; // 90 degrees about y: x -> -z
  const m = compose([1, 2, 3], q, [2, 2, 2]);
  assert.ok(near(apply(m, [1, 0, 0]), [1, 2, 1]));
  const p = mul(compose([10, 0, 0]), m); // parent moves the child
  assert.ok(near(apply(p, [1, 0, 0]), [11, 2, 1]));
  assert.ok(near(mul(compose(), m), m));
});

test('leafKind follows look.js: a Leaf_ or needle material without alpha is flat, cut-out alpha is leaf', () => {
  assert.equal(leafKind({ name: 'Leaf_WhitePine' }), 'flat');
  assert.equal(leafKind({ name: 'pine_needles' }), 'flat');
  assert.equal(leafKind({ name: 'Leaf_RedMaple_v2', alphaMode: 'MASK' }), 'leaf');
  assert.equal(leafKind({ name: 'Glass', alphaMode: 'BLEND' }), null); // blend without an image is glass, not foliage
  assert.equal(leafKind({ name: 'Ivy', alphaMode: 'BLEND', pbrMetallicRoughness: { baseColorTexture: { index: 0 } } }), 'leaf');
  assert.equal(leafKind({ name: 'Bark_Maple' }), null);
});

test('treeGroups keeps whole trees as trees.js groups them, and leaves shrubs and single copies out', () => {
  const bark = { name: 'Bark_Maple' }, leaf = { name: 'Leaf_Maple', alphaMode: 'MASK' }, shrub = { name: 'Leaf_Shrub_Yew', alphaMode: 'MASK' };
  const g = treeGroups([
    { node: 0, parent: -1, count: 4, name: 'Tree_A', prims: [{ material: bark, name: 'Tree_A' }, { material: leaf, name: 'Tree_A' }] },
    { node: 1, parent: -1, count: 1, name: 'Tree_B', prims: [{ material: bark }, { material: leaf }] }, // one copy: not instanced in the viewer
    { node: 2, parent: -1, count: 9, name: 'Shrub_Yew', prims: [{ material: shrub }] }, // leaf only
    { node: 3, parent: 7, count: 3, name: 'Tree_C_bark', prims: [{ material: bark }] }, // one tree split over two nodes
    { node: 4, parent: 7, count: 3, name: 'Tree_C_leaf', prims: [{ material: leaf }] },
    { node: 5, parent: -1, count: 5, name: 'ShrubCore', prims: [{ material: bark, name: 'ShrubCore' }, { material: leaf, name: 'ShrubCore' }] },
  ]);
  assert.deepEqual(g.map(x => [x.first, x.count, x.prims.length, x.crowns.length]), [[0, 4, 2, 1], [3, 3, 2, 1]]);
});

test('record: crown centre and half-size, trunk base and half height in world metres, as trees.js add()', () => {
  const m = compose([100, 50, -20], [0, 0, 0, 1], [2, 2, 2]);
  const r = record(m, { min: [-1, 2, -1], max: [1, 6, 1] }, { min: [-1, 0, -1], max: [1, 6, 1] }, [0.1, 0.2, 0.3]);
  assert.equal(r.length, 13);
  assert.ok(near(r, [100, 58, -20, 2, 4, 2, 100, 50, -20, 6, 0.1, 0.2, 0.3]));
  const mirrored = record(compose(undefined, undefined, [-1, 1, 1]), { min: [-1, 0, -1], max: [1, 2, 1] }, { min: [-1, 0, -1], max: [1, 2, 1] }, [0, 0, 0]);
  assert.equal(mirrored[3], -1); // Matrix4.decompose negates x of a mirrored matrix, and trees.js uses it as it is
});

test('leafColour follows trees.js: material colour times the mean opaque pixel, a little darker', () => {
  assert.ok(near(leafColour({ name: 'Leaf_WhitePine' }, null), srgbToLinear([0x4f, 0x5a, 0x33]).map(v => v * 0.6)));
  const mask = { name: 'Leaf_X', alphaMode: 'MASK', pbrMetallicRoughness: { baseColorFactor: [0.5, 1, 1, 1] } };
  assert.ok(near(leafColour(mask, null), [0.3, 0.6, 0.6]));
  const px = new Uint8Array([255, 255, 255, 255, 0, 0, 0, 0]); // one opaque white pixel, one clear one ignored
  assert.ok(near(leafColour(mask, px), [0.4, 0.8, 0.8]));
  assert.ok(near(leafColour(mask, new Uint8Array(8)), [0.5 * 0.25 * 0.8, 0.35 * 0.8, 0.18 * 0.8])); // nothing opaque
});
