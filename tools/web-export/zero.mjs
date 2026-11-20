// Pure helpers for drop_zero.mjs: find triangles that draw nothing. No dependencies, unit-tested from node --test.
// build_web.sh copies this file next to drop_zero.mjs before it runs it.

/**
 * True when the triangle a, b, c (vertex indices into `pos`, 3 numbers a vertex, as stored: quantized
 * integers or floats) has zero area: two corners at the same place or all three on one line. The test is
 * exact on the stored numbers, so it holds after any node or instance transform.
 */
export function zeroArea(pos, a, b, c) {
  if (a === b || b === c || a === c) return true;
  a *= 3; b *= 3; c *= 3;
  const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
  const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
  return uy * vz - uz * vy === 0 && uz * vx - ux * vz === 0 && ux * vy - uy * vx === 0;
}

/** The index list without its zero-area triangles, same type and order; null when there are none. */
export function keepTriangles(index, pos) {
  const keep = [];
  let dropped = 0;
  for (let i = 0; i + 2 < index.length; i += 3) {
    if (zeroArea(pos, index[i], index[i + 1], index[i + 2])) { dropped++; continue; }
    keep.push(index[i], index[i + 1], index[i + 2]);
  }
  return dropped ? new index.constructor(keep) : null;
}
