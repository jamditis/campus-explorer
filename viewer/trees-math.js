// Pure. Far-field trees ([x, y, z, crown radius, height] per tree, three.js axes, models/main far_trees.bin)
// grouped in square ground cells, so trees.js can draw one instanced mesh per cell with its own bounding
// sphere: frustum culling then skips the cells out of view, in the view and in the shadow map.

/** Side of a far-tree cell, metres. */
export const FAR_CELL = 500;

/** Map of "i,j" cell key -> indices of the trees in it, in input order. */
export function farCells(a, cell = FAR_CELL) {
  const out = new Map(), n = Math.floor(a.length / 5);
  for (let i = 0; i < n; i++) {
    const k = `${Math.floor(a[i * 5] / cell)},${Math.floor(a[i * 5 + 2] / cell)}`;
    if (!out.has(k)) out.set(k, []);
    out.get(k).push(i);
  }
  return out;
}

/**
 * Floats per tree in a stand-in record: crown centre (3), crown half-size (3), trunk base (3), half the tree's
 * height (1), leaf colour, linear RGB (3). World axes, metres. trees.js builds one per instance of a full tile;
 * tools/web-export/tree_points.mjs writes them into a far version (scene extras `trees`) for a tile not in memory.
 */
export const STAND_IN = 13;

/** The impostor of record `i` in `a`: crown centre and size, trunk base, height and width, culling radius, colour. */
export function standIn(a, i = 0) {
  const o = i * STAND_IN, sx = a[o + 3], sy = a[o + 4], sz = a[o + 5], cy = a[o + 1], by = a[o + 7];
  return {
    c: [a[o], cy, a[o + 2]],
    s: [sx * 0.95, sy * 0.95, sz * 0.95],
    base: [a[o + 6], by, a[o + 8]],
    trunkH: Math.max(0.5, cy - sy * 0.6 - by),
    trunkW: Math.max(0.12, Math.min(sx, sz) * 0.08),
    rad: Math.max(sx, sy, sz, a[o + 9]),
    col: [a[o + 10], a[o + 11], a[o + 12]],
  };
}
