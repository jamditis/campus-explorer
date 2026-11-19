// Tile load order. Pure: no imports, no DOM.
// Tile centres are [x, z] in three.js viewer metres (x east, -z grid north); each tile is a
// TILE_SIZE square around its centre.

/** Edge length of a tile square, metres. */
export const TILE_SIZE = 160;

const HALF = TILE_SIZE / 2;
// Ahead-of-viewer weighting for the tie-break key: 0.7x straight ahead, 1.3x straight behind.
const AHEAD_WEIGHT = 0.3;

function hasCentre(tile) {
  const c = tile && tile.center;
  return Array.isArray(c) && c.length >= 2 && Number.isFinite(c[0]) && Number.isFinite(c[1]);
}

function isSkirt(tile) {
  const file = tile && typeof tile.file === 'string' ? tile.file : '';
  return file === 'skirt.glb' || file.endsWith('/skirt.glb');
}

function contains(tile, x, z) {
  return Math.abs(x - tile.center[0]) <= HALF && Math.abs(z - tile.center[1]) <= HALF;
}

function unitDir(dir) {
  if (!dir || !Number.isFinite(dir.x) || !Number.isFinite(dir.z)) return null;
  const len = Math.hypot(dir.x, dir.z);
  return len > 0 ? { x: dir.x / len, z: dir.z / len } : null;
}

/**
 * Distance in metres on the ground plane (x, z in viewer metres) from a point to a tile's
 * square; 0 when the point is inside or on the edge. Infinity for a tile with no centre.
 */
export function squareDistance(tile, x, z) {
  if (!hasCentre(tile)) return Infinity;
  const dx = Math.max(Math.abs(x - tile.center[0]) - HALF, 0);
  const dz = Math.max(Math.abs(z - tile.center[1]) - HALF, 0);
  return Math.hypot(dx, dz);
}

/**
 * Load order for tiles. focus = { x, z } in viewer metres; dir = unit view direction
 * { x, z } on the ground plane, or null. No-centre tiles first in manifest order, then the
 * tile containing the focus, then nearest square first with tiles ahead winning ties.
 * Returns a new array; equal keys keep manifest order.
 */
export function orderTiles(tiles, focus, dir = null) {
  if (!Array.isArray(tiles)) return [];
  const fx = focus && Number.isFinite(focus.x) ? focus.x : 0;
  const fz = focus && Number.isFinite(focus.z) ? focus.z : 0;
  const d = unitDir(dir);
  const plain = [];
  const keyed = [];
  tiles.forEach((tile, index) => {
    if (!hasCentre(tile)) {
      plain.push(tile);
      return;
    }
    const tx = tile.center[0] - fx;
    const tz = tile.center[1] - fz;
    const centreDist = Math.hypot(tx, tz);
    let tie = centreDist;
    if (d && centreDist > 0) {
      const cos = (tx * d.x + tz * d.z) / centreDist;
      tie = centreDist * (1 - AHEAD_WEIGHT * cos);
    }
    keyed.push({
      tile,
      index,
      inside: contains(tile, fx, fz) ? 0 : 1,
      // Round to 1 cm so float noise does not hide genuine ties from the tie-break.
      dist: Math.round(squareDistance(tile, fx, fz) * 100),
      tie,
    });
  });
  keyed.sort((a, b) => a.inside - b.inside || a.dist - b.dist || a.tie - b.tie || a.index - b.index);
  return plain.concat(keyed.map((k) => k.tile));
}

/**
 * Tiles needed before the view is shown: every no-centre 'skirt.glb', then the `count`
 * nearest centred tiles to focus = { x, z } (viewer metres), the one containing it first.
 */
export function firstBatch(tiles, focus, count) {
  if (!Array.isArray(tiles)) return [];
  const n = Number.isFinite(count) ? Math.max(0, Math.floor(count)) : 0;
  const skirts = tiles.filter((t) => !hasCentre(t) && isSkirt(t));
  const nearest = orderTiles(tiles.filter(hasCentre), focus).slice(0, n);
  return skirts.concat(nearest);
}

/**
 * The centred tile whose square contains the point (x, z in viewer metres), or null.
 * A point on a shared edge goes to the first such tile in manifest order.
 */
export function tileAt(tiles, x, z) {
  if (!Array.isArray(tiles) || !Number.isFinite(x) || !Number.isFinite(z)) return null;
  return tiles.find((t) => hasCentre(t) && contains(t, x, z)) || null;
}

/**
 * Union of the centred tiles' squares in viewer metres (x east, z south), or null when
 * there are none.
 */
export function boundsOf(tiles) {
  if (!Array.isArray(tiles)) return null;
  let b = null;
  for (const t of tiles) {
    if (!hasCentre(t)) continue;
    const [cx, cz] = t.center;
    if (!b) b = { minX: Infinity, maxX: -Infinity, minZ: Infinity, maxZ: -Infinity };
    b.minX = Math.min(b.minX, cx - HALF);
    b.maxX = Math.max(b.maxX, cx + HALF);
    b.minZ = Math.min(b.minZ, cz - HALF);
    b.maxZ = Math.max(b.maxZ, cz + HALF);
  }
  return b;
}
