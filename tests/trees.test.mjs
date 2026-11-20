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
