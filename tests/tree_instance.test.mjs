import { test } from 'node:test';
import assert from 'node:assert/strict';
import { isTreeMesh, treeBatches } from '../tools/web-export/pack.mjs';

test('tree meshes are the shared Tree_* meshes, nothing else', () => {
  assert.ok(isTreeMesh('Tree_RedMaple_LOD1_v2Oct'));
  assert.ok(isTreeMesh('Tree_PinOak_LOD1_v2Oct_limb24_ws149_2.5'));
  for (const n of ['SW_V_trees_Tree_036_UNVERIFIEDspecies', 'Lamp_Post_Acorn_Period', 'bench_wood',
    'Leaf_Shrub_01', 'tree_impostors', 'Tree_Shrub_boxwood', '', undefined]) assert.ok(!isTreeMesh(n), n);
});

test('a tree mesh used by two or more nodes becomes one batch of those nodes', () => {
  const nodes = [
    { mesh: 'a', name: 'Tree_RedMaple' }, { mesh: 'b', name: 'Tree_PinOak' },
    { mesh: 'a', name: 'Tree_RedMaple' }, { mesh: null }, { mesh: 'b', name: 'Tree_PinOak' },
    { mesh: 'a', name: 'Tree_RedMaple' }, { mesh: 'c', name: 'Tree_WhitePine' },
  ];
  assert.deepEqual(treeBatches(nodes), [[0, 2, 5], [1, 4]]); // Tree_WhitePine is used once
});

test('fixtures in small groups are left to optimize (joined, with collision)', () => {
  const lamp = { mesh: 'l', name: 'Lamp_Post' }, bench = { mesh: 'b', name: 'bench' };
  const nodes = [lamp, lamp, lamp, bench, bench];
  assert.deepEqual(treeBatches(nodes), []);
});

test('meshes are told apart by identity, not by name', () => {
  // two different meshes can carry the same name (Blender appends .001 only within one file)
  const nodes = [{ mesh: 'a', name: 'Tree_X' }, { mesh: 'b', name: 'Tree_X' }, { mesh: 'a', name: 'Tree_X' }];
  assert.deepEqual(treeBatches(nodes), [[0, 2]]);
});

test('skinned nodes and nodes that are already instances are not batched', () => {
  const nodes = [{ mesh: 'a', name: 'Tree_A' }, { mesh: 'a', name: 'Tree_A', skin: true },
    { mesh: 'b', name: 'Tree_B', instanced: true }, { mesh: 'b', name: 'Tree_B' },
    { mesh: 'b', name: 'Tree_B' }];
  assert.deepEqual(treeBatches(nodes), [[3, 4]]);
});

test('a larger minimum keeps smaller groups out', () => {
  const nodes = [{ mesh: 'a', name: 'Tree_A' }, { mesh: 'a', name: 'Tree_A' }];
  assert.deepEqual(treeBatches(nodes, 3), []);
});
