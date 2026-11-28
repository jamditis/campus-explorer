import test from 'node:test';
import assert from 'node:assert/strict';
import { farCells, FAR_CELL } from '../viewer/trees-math.js';

// far trees: [x, y, z, crown radius, height] per tree, three.js axes
const A = new Float32Array([
  10, 100, 10, 3, 9, // cell 0,0
  490, 100, 20, 3, 9, // cell 0,0
  510, 100, 20, 3, 9, // cell 1,0
  -10, 100, -600, 3, 9, // cell -1,-2
  20, 100, 30, 3, 9, // cell 0,0
]);

test('far trees are grouped in square cells of FAR_CELL metres, each tree once, in input order', () => {
  assert.equal(FAR_CELL, 500);
  const cells = farCells(A);
  assert.deepEqual([...cells.keys()].sort(), ['-1,-2', '0,0', '1,0']);
  assert.deepEqual(cells.get('0,0'), [0, 1, 4]);
  assert.deepEqual(cells.get('1,0'), [2]);
  assert.deepEqual(cells.get('-1,-2'), [3]);
  assert.equal([...cells.values()].flat().length, 5);
});

test('a cell size can be given, and an empty or ragged array gives no cells', () => {
  assert.equal(farCells(A, 2000).size, 2); // -600 falls in the cell below zero
  assert.equal(farCells(new Float32Array(0)).size, 0);
  assert.equal(farCells(new Float32Array(4)).size, 0);
});

test('a stand-in record gives the impostor trees.js draws: crown, trunk, culling radius, colour', async () => {
  const { standIn, STAND_IN } = await import('../viewer/trees-math.js');
  assert.equal(STAND_IN, 13);
  // crown centre (0, 10, 0), half-size 3 x 4 x 2, base at y 0, half height 7, colour
  const a = new Float32Array([5, 5, 5, 1, 1, 1, 5, 4, 5, 1, 0, 0, 0, 0, 10, 0, 3, 4, 2, 0, 0, 0, 7, 0.1, 0.2, 0.3]);
  const t = standIn(a, 1);
  assert.deepEqual(t.c, [0, 10, 0]);
  assert.deepEqual(t.s.map(v => +v.toFixed(4)), [2.85, 3.8, 1.9]);
  assert.deepEqual(t.base, [0, 0, 0]);
  assert.equal(+t.trunkH.toFixed(4), 7.6); // 10 - 4 * 0.6
  assert.equal(+t.trunkW.toFixed(4), 0.16); // min(3, 2) * 0.08
  assert.equal(t.rad, 7); // the half height is the largest
  assert.deepEqual(t.col.map(v => +v.toFixed(4)), [0.1, 0.2, 0.3]);
  const small = standIn(a, 0); // a low crown keeps a 0.5 m trunk, a thin one 0.12 m
  assert.equal(small.trunkH, 0.5); assert.equal(+small.trunkW.toFixed(4), 0.12);
});
