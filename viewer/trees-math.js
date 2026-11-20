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
