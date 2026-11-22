// Pure. The middle levels of detail of trees and the thinned shrub leaf cards (trees.js), without three.js.
//
// Trees: most bark triangles are twigs (on the sw16 tiles, 86 % of the bark triangles of the unique tree meshes
// are in pieces under 6 cm thick), and a twig costs as many triangles as a limb. Each bark mesh is reordered
// once: pieces at least BARK_MIN_DIAMETER thick first, then the thin pieces from the largest to the smallest
// area. A middle version is the same buffers drawn over a shorter range, so it costs no download and no GPU
// memory, and leaves its leaves whole. Two of them:
//   - from TREE_MID: the smallest thin pieces go, together at most BARK_SHARE.near of the bark's area;
//   - from TREE_FAR_MID: every thin piece goes (BARK_SHARE.far).
// A thin piece is under a pixel wide where it goes (see tests/treelod.test.mjs), but antialiasing still shows a
// sub-pixel branch as a faint line, so what goes is limited by its area as well: on a rendered honey locust, the
// sparsest crown here, the first step changes the tree's pixels by 1.4/255 on average.
//
// Shrubs: each shrub is a core and thousands of instanced leaf cards of 2 x 5 cm. Past SHRUB_REACH (from the
// camera to the box of a card batch) one card in SHRUB_THIN is drawn, grown by sqrt(SHRUB_THIN) about its own
// origin: the same covered area from fewer cards, where a card is under a pixel either way.

/** Distance (m) from which a tree is drawn as its first middle version, per quality level. */
export const TREE_MID = { low: 50, medium: 70, high: 100 };
/** Distance (m) from which a tree is drawn as its second middle version (no thin bark), per quality level. */
export const TREE_FAR_MID = { low: 120, medium: 170, high: 250 };
/** Bark pieces thinner than this (world metres, estimated per connected piece) may be left out. */
export const BARK_MIN_DIAMETER = 0.06;
/** Most of the bark's area the thin pieces left out of each middle version may hold. */
export const BARK_SHARE = { near: 0.1, far: 1 };
/** Distance (m) from the camera to a shrub leaf-card batch's box past which its cards are thinned, per quality. */
export const SHRUB_REACH = { low: 35, medium: 45, high: 60 };
/** One shrub leaf card in this many is drawn past SHRUB_REACH. */
export const SHRUB_THIN = 8;

/**
 * Order the triangles of a bark mesh for its middle versions: pieces at least `minDiameter` thick first (in
 * their own order), then the thinner pieces from the largest area to the smallest.
 * A piece is a set of triangles joined by shared vertex positions (welded, so a branch split at its UV seams
 * is one piece). Its diameter is estimated as a tube's: area / (pi * length), the length being the diagonal of
 * its box, all times `scale` (mesh units to world metres; pass the largest scale the mesh is drawn at, so no
 * instance loses a branch thicker than `minDiameter`). A curved branch has a shorter box than its length, so
 * its estimate is too thick, never too thin.
 * `kept[i]` is how many triangles of the order to draw when the thin pieces left out may hold at most
 * `shares[i]` of the bark's area (the smallest go first), so every version is a prefix of the order.
 * @returns {{ order: Uint32Array, kept: number[] }}
 */
export function barkOrder(position, index, { minDiameter, scale = 1, shares = [1] }) {
  const nv = Math.floor(position.length / 3), nt = Math.floor(index.length / 3);
  if (!nt) return { order: new Uint32Array(0), kept: shares.map(() => 0) };
  const parent = new Int32Array(nv);
  for (let i = 0; i < nv; i++) parent[i] = i;
  const find = i => { while (parent[i] !== i) { parent[i] = parent[parent[i]]; i = parent[i]; } return i; };
  const join = (a, b) => { a = find(a); b = find(b); if (a !== b) parent[a] = b; };
  // weld: vertices at exactly the same position (open-addressing table on the float bits)
  const bits = new Uint32Array(Float32Array.from(position.subarray(0, nv * 3)).buffer);
  let size = 1; while (size < nv * 2) size <<= 1;
  const slot = new Int32Array(size).fill(-1), mask = size - 1;
  for (let i = 0; i < nv; i++) {
    const x = bits[i * 3], y = bits[i * 3 + 1], z = bits[i * 3 + 2];
    let h = (Math.imul(x, 0x9e3779b1) ^ Math.imul(y, 0x85ebca77) ^ Math.imul(z, 0xc2b2ae3d)) & mask;
    for (;;) {
      const j = slot[h];
      if (j < 0) { slot[h] = i; break; }
      if (bits[j * 3] === x && bits[j * 3 + 1] === y && bits[j * 3 + 2] === z) { join(i, j); break; }
      h = (h + 1) & mask;
    }
  }
  for (let t = 0; t < nt; t++) { join(index[t * 3], index[t * 3 + 1]); join(index[t * 3], index[t * 3 + 2]); }
  // area and box per piece
  const area = new Float64Array(nv), lo = new Float64Array(nv * 3).fill(Infinity), hi = new Float64Array(nv * 3).fill(-Infinity);
  const root = new Int32Array(nt);
  for (let t = 0; t < nt; t++) {
    const a = index[t * 3] * 3, b = index[t * 3 + 1] * 3, c = index[t * 3 + 2] * 3, r = root[t] = find(index[t * 3]);
    const ux = position[b] - position[a], uy = position[b + 1] - position[a + 1], uz = position[b + 2] - position[a + 2];
    const vx = position[c] - position[a], vy = position[c + 1] - position[a + 1], vz = position[c + 2] - position[a + 2];
    area[r] += Math.hypot(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx) / 2;
    for (let k = 0; k < 3; k++) {
      const pa = position[a + k], pb = position[b + k], pc = position[c + k];
      const mn = pa < pb ? (pa < pc ? pa : pc) : (pb < pc ? pb : pc), mx = pa > pb ? (pa > pc ? pa : pc) : (pb > pc ? pb : pc);
      if (mn < lo[r * 3 + k]) lo[r * 3 + k] = mn;
      if (mx > hi[r * 3 + k]) hi[r * 3 + k] = mx;
    }
  }
  // pieces: thick ones keep their place, thin ones sort by area, largest first
  const seen = new Uint8Array(nv), rank = new Int32Array(nv).fill(-1), thin = [], tris = new Int32Array(nv);
  let total = 0;
  for (let t = 0; t < nt; t++) {
    const r = root[t];
    tris[r]++;
    if (seen[r]) continue;
    seen[r] = 1; total += area[r];
    const len = Math.hypot(hi[r * 3] - lo[r * 3], hi[r * 3 + 1] - lo[r * 3 + 1], hi[r * 3 + 2] - lo[r * 3 + 2]);
    if (!(len > 0) || area[r] * scale / (Math.PI * len) < minDiameter) thin.push(r);
  }
  thin.sort((a, b) => area[b] - area[a] || a - b);
  thin.forEach((r, i) => { rank[r] = i; });
  const order = new Uint32Array(nt);
  let thick = 0;
  for (let t = 0; t < nt; t++) if (rank[root[t]] < 0) order[thick++] = t;
  // thin triangles grouped by piece in rank order (counting sort), each piece's triangles in their own order
  const start = new Int32Array(thin.length + 1);
  for (let i = 0; i < thin.length; i++) start[i + 1] = start[i] + tris[thin[i]];
  const fill = start.slice(0, thin.length);
  for (let t = 0; t < nt; t++) { const k = rank[root[t]]; if (k >= 0) order[thick + fill[k]++] = t; }
  // for each share: drop from the smallest piece up while what goes holds at most that share of the area
  const kept = shares.map(share => {
    let gone = 0, k = thin.length;
    while (k > 0 && gone + area[thin[k - 1]] <= share * total) gone += area[thin[--k]];
    return thick + start[k];
  });
  return { order, kept };
}

/** A copy of `index` (same array type) with its triangles in `order`. */
export function reorderIndex(index, order) {
  const out = new index.constructor(order.length * 3);
  for (let i = 0; i < order.length; i++) {
    const t = order[i] * 3;
    out[i * 3] = index[t]; out[i * 3 + 1] = index[t + 1]; out[i * 3 + 2] = index[t + 2];
  }
  return out;
}

/**
 * About one in `k` of `n` instances, picked by a hash of the index (instances often come in runs per shrub, so
 * every k-th would follow their order), ascending. Never empty when n > 0.
 */
export function thinPick(n, k) {
  if (k <= 1) return Uint32Array.from({ length: n }, (_, i) => i);
  const out = [];
  for (let i = 0; i < n; i++) {
    let h = Math.imul(i ^ 0x9e3779b9, 0x85ebca6b); h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35); h ^= h >>> 16;
    if ((h >>> 0) % k === 0) out.push(i);
  }
  if (!out.length && n > 0) out.push(0);
  return Uint32Array.from(out);
}

/** Scale the 3x3 part of the column-major 4x4 matrix at `offset` in `m` by `f`, in place (about the instance origin). */
export function scaleLinear(m, offset, f) {
  for (let c = 0; c < 3; c++) for (let r = 0; r < 3; r++) m[offset + c * 4 + r] *= f;
  return m;
}

/** On-screen size in pixels of `size` metres at `d` metres, for a vertical field of view `fov` degrees over `height` px. */
export function pixels(size, d, fov, height) {
  return size / d / (2 * Math.tan(fov * Math.PI / 360)) * height;
}

/**
 * Which version of a tree draws at distance `d`: 0 full, 1 first middle (from `mid`), 2 second middle (from
 * `farMid`), 3 impostor (from `dist`). A band whose start lies past a later one's is skipped.
 */
export function treeBand(d, mid, farMid, dist) {
  return d >= dist ? 3 : d >= farMid ? 2 : d >= mid ? 1 : 0;
}

/** Run `build(geo)` with the geometry's whole index range in place, then put the drawn range back.
 *  A collision structure is built from the range drawn now (three-mesh-bvh reads `drawRange`), and a
 *  tree at middle distance draws only its thick branches: built then, the twigs would be missing
 *  from picking and measuring for good. */
export function withFullRange(geo, build) {
  const { start, count } = geo.drawRange;
  geo.drawRange.start = 0; geo.drawRange.count = Infinity;
  try { return build(geo); } finally { geo.drawRange.start = start; geo.drawRange.count = count; }
}
