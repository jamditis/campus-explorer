import test from 'node:test';
import assert from 'node:assert/strict';
import { TILE_SIZE, orderTiles, firstBatch, tileAt, boundsOf, squareDistance } from '../viewer/schedule.js';

const tile = (i, j) => ({ file: `t_${i}_${j}.glb`, bytes: 1, center: [i * TILE_SIZE, j * TILE_SIZE] });
const skirt = { file: 'skirt.glb', bytes: 1 };
const context = { file: 'context.glb', bytes: 1, center: null };

function grid(n) {
  const out = [];
  for (let i = -n; i <= n; i++) for (let j = -n; j <= n; j++) out.push(tile(i, j));
  return out;
}

const names = (tiles) => tiles.map((t) => t.file);

test('tile size is 160 m', () => {
  assert.equal(TILE_SIZE, 160);
});

test('squareDistance is 0 inside and on the edge', () => {
  const t = tile(0, 0);
  assert.equal(squareDistance(t, 0, 0), 0);
  assert.equal(squareDistance(t, 80, -80), 0);
  assert.equal(squareDistance(t, 90, 0), 10);
  assert.equal(squareDistance(t, 83, 84), 5);
  assert.equal(squareDistance(skirt, 0, 0), Infinity);
});

test('no-centre tiles come first in manifest order', () => {
  const tiles = [tile(1, 0), context, tile(0, 0), skirt];
  const out = orderTiles(tiles, { x: 0, z: 0 });
  assert.deepEqual(names(out), ['context.glb', 'skirt.glb', 't_0_0.glb', 't_1_0.glb']);
  assert.notEqual(out, tiles);
  assert.deepEqual(names(tiles), ['t_1_0.glb', 'context.glb', 't_0_0.glb', 'skirt.glb']);
});

test('nearest square first, focus tile first', () => {
  const out = orderTiles(grid(2), { x: 170, z: 10 });
  assert.equal(out[0].file, 't_1_0.glb');
  for (let k = 1; k < out.length; k++) {
    assert.ok(
      Math.round(squareDistance(out[k - 1], 170, 10) * 100) <= Math.round(squareDistance(out[k], 170, 10) * 100),
    );
  }
});

test('focus on a shared edge: the containing tiles sort first', () => {
  const out = orderTiles(grid(1), { x: 80, z: 0 });
  assert.deepEqual(names(out.slice(0, 2)).sort(), ['t_0_0.glb', 't_1_0.glb']);
});

test('tiles ahead win ties over tiles behind', () => {
  const tiles = [tile(-1, 0), tile(0, -1), tile(0, 0), tile(0, 1), tile(1, 0)];
  // Looking grid north (-z).
  const north = orderTiles(tiles, { x: 0, z: 0 }, { x: 0, z: -1 });
  assert.deepEqual(names(north), ['t_0_0.glb', 't_0_-1.glb', 't_-1_0.glb', 't_1_0.glb', 't_0_1.glb']);
  const east = orderTiles(tiles, { x: 0, z: 0 }, { x: 1, z: 0 });
  assert.equal(east[1].file, 't_1_0.glb');
  assert.equal(east[4].file, 't_-1_0.glb');
});

test('direction does not override a nearer tile', () => {
  const tiles = [tile(3, 0), tile(-1, 0)];
  const out = orderTiles(tiles, { x: 0, z: 0 }, { x: 1, z: 0 });
  assert.deepEqual(names(out), ['t_-1_0.glb', 't_3_0.glb']);
});

test('a tile containing the focus sorts first even when behind', () => {
  const tiles = [tile(1, 0), tile(0, 0)];
  const out = orderTiles(tiles, { x: 10, z: 0 }, { x: -1, z: 0 });
  assert.equal(out[0].file, 't_0_0.glb');
});

test('unnormalised or zero direction is handled', () => {
  const tiles = [tile(-1, 0), tile(1, 0)];
  assert.deepEqual(names(orderTiles(tiles, { x: 0, z: 0 }, { x: 5, z: 0 })), ['t_1_0.glb', 't_-1_0.glb']);
  assert.deepEqual(names(orderTiles(tiles, { x: 0, z: 0 }, { x: 0, z: 0 })), ['t_-1_0.glb', 't_1_0.glb']);
});

test('stable for equal keys', () => {
  const a = { ...tile(1, 0), file: 'a.glb' };
  const b = { ...tile(1, 0), file: 'b.glb' };
  assert.deepEqual(names(orderTiles([b, a], { x: 0, z: 0 })), ['b.glb', 'a.glb']);
  assert.deepEqual(names(orderTiles([a, b], { x: 0, z: 0 })), ['a.glb', 'b.glb']);
});

test('empty and bad input', () => {
  assert.deepEqual(orderTiles([], { x: 0, z: 0 }), []);
  assert.deepEqual(orderTiles(null, { x: 0, z: 0 }), []);
  assert.deepEqual(firstBatch([], { x: 0, z: 0 }, 4), []);
  assert.equal(tileAt([], 0, 0), null);
  assert.equal(boundsOf([]), null);
  assert.equal(boundsOf([skirt, context]), null);
});

test('firstBatch: skirt plus the nearest tiles, focus tile first, no context', () => {
  const tiles = [context, ...grid(2), skirt];
  const out = firstBatch(tiles, { x: 5, z: -5 }, 3);
  assert.equal(out.length, 4);
  assert.equal(out[0].file, 'skirt.glb');
  assert.equal(out[1].file, 't_0_0.glb');
  assert.ok(!out.includes(context));
  assert.deepEqual(names(firstBatch(tiles, { x: 0, z: 0 }, 0)), ['skirt.glb']);
  assert.equal(firstBatch(tiles, { x: 0, z: 0 }, 1000).length, 26);
});

test('tileAt finds the containing tile', () => {
  const tiles = [skirt, ...grid(1)];
  assert.equal(tileAt(tiles, 0, 0).file, 't_0_0.glb');
  assert.equal(tileAt(tiles, 200, -200).file, 't_1_-1.glb');
  assert.equal(tileAt(tiles, 241, 0), null);
  assert.equal(tileAt(tiles, NaN, 0), null);
});

test('boundsOf is the union of squares', () => {
  const tiles = [skirt, tile(0, 0), tile(2, -1)];
  assert.deepEqual(boundsOf(tiles), { minX: -80, maxX: 400, minZ: -240, maxZ: 80 });
});
