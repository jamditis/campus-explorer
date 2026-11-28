// Pure parts of tree_points.mjs: which instanced nodes of a tile make one tree group the way the viewer sees them
// (trees.js add(), with look.js's leaf rule), and the stand-in record of one instance (viewer/trees-math.js STAND_IN).
// Matrices are 16 numbers, column-major, as in glTF.

/** a * b */
export function mul(a, b) {
  const o = new Array(16);
  for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
    o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3];
  }
  return o;
}

/** Matrix of translation t, unit quaternion q (x, y, z, w) and scale s. */
export function compose(t = [0, 0, 0], q = [0, 0, 0, 1], s = [1, 1, 1]) {
  const [x, y, z, w] = q, x2 = x + x, y2 = y + y, z2 = z + z;
  const xx = x * x2, xy = x * y2, xz = x * z2, yy = y * y2, yz = y * z2, zz = z * z2, wx = w * x2, wy = w * y2, wz = w * z2;
  return [
    (1 - (yy + zz)) * s[0], (xy + wz) * s[0], (xz - wy) * s[0], 0,
    (xy - wz) * s[1], (1 - (xx + zz)) * s[1], (yz + wx) * s[1], 0,
    (xz + wy) * s[2], (yz - wx) * s[2], (1 - (xx + yy)) * s[2], 0,
    t[0], t[1], t[2], 1,
  ];
}

export const apply = (m, [x, y, z]) => [
  m[0] * x + m[4] * y + m[8] * z + m[12], m[1] * x + m[5] * y + m[9] * z + m[13], m[2] * x + m[6] * y + m[10] * z + m[14],
];

/**
 * How look.js treats a glTF material: 'flat' (a Leaf_ or needle material with no alpha: drawn solid #4f5a33,
 * its image dropped), 'leaf' (cut out by alpha) or null (not foliage).
 */
export function leafKind(mat = {}) {
  const mode = mat.alphaMode ?? 'OPAQUE', map = !!mat.pbrMetallicRoughness?.baseColorTexture;
  if (/^Leaf_|needle/i.test(mat.name ?? '') && mode === 'OPAQUE') return 'flat';
  if (mode === 'MASK' || (mode === 'BLEND' && map)) return 'leaf';
  return null;
}

/**
 * Tree groups of a glTF scene as trees.js forms them. GLTFLoader makes a node of several primitives a group of
 * instanced meshes and a node of one primitive a single instanced mesh under the node's parent; trees.js keys
 * the instanced meshes by parent and instance count. A group needs leaf and non-leaf meshes and no shrub.
 * `nodes`: [{ node, parent, count, name, prims: [{ material, name }] }] for the instanced nodes, in scene order.
 * Returns [{ first (node index whose matrices count), count, prims: [...], crowns: [...] }].
 */
export function treeGroups(nodes) {
  const by = new Map();
  for (const n of nodes) {
    if (n.count < 2) continue;
    const key = n.prims.length > 1 ? `n${n.node}` : `p${n.parent}:${n.count}`;
    if (!by.has(key)) by.set(key, { first: n.node, count: n.count, prims: [], names: [] });
    const g = by.get(key); g.prims.push(...n.prims); g.names.push(...(n.prims.length > 1 ? n.prims.map(p => p.name) : [n.name]));
  }
  const out = [];
  for (const g of by.values()) {
    const crowns = g.prims.filter(p => leafKind(p.material));
    if (!crowns.length || crowns.length === g.prims.length || g.names.some(s => /shrub/i.test(s ?? ''))) continue;
    out.push({ first: g.first, count: g.count, prims: g.prims, crowns });
  }
  return out;
}

/**
 * Stand-in record (STAND_IN floats) of one instance: world matrix `m` (node world * instance), crown box and
 * tree box in instance space ({ min, max }), linear leaf colour. Same numbers as trees.js add().
 */
export function record(m, crown, tree, col) {
  const cc = [0, 1, 2].map(k => (crown.min[k] + crown.max[k]) / 2), cs = [0, 1, 2].map(k => crown.max[k] - crown.min[k]);
  // scale of each axis (Matrix4.decompose: column lengths, x negated for a mirrored matrix)
  const len = k => Math.hypot(m[k * 4], m[k * 4 + 1], m[k * 4 + 2]);
  const det = m[0] * (m[5] * m[10] - m[9] * m[6]) - m[4] * (m[1] * m[10] - m[9] * m[2]) + m[8] * (m[1] * m[6] - m[5] * m[2]);
  const s = [det < 0 ? -len(0) : len(0), len(1), len(2)];
  const c = apply(m, cc), base = apply(m, [cc[0], tree.min[1], cc[2]]);
  return [...c, cs[0] * s[0] / 2, cs[1] * s[1] / 2, cs[2] * s[2] / 2, ...base, (tree.max[1] - tree.min[1]) * s[1] / 2, ...col];
}

const lin = v => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
/** sRGB 0..255 triple -> linear 0..1 */
export const srgbToLinear = rgb => rgb.map(v => lin(v / 255));

/**
 * Impostor colour of a leaf material as trees.js leafColour() gives it: material colour (linear) times the mean
 * of the image's opaque pixels at 16 x 16 (`rgba`, or null with no image), a little darker; a flat leaf is
 * #4f5a33 at 0.6, an image with no opaque pixel a fixed green.
 */
export function leafColour(mat, rgba) {
  if (leafKind(mat) === 'flat') return srgbToLinear([0x4f, 0x5a, 0x33]).map(v => v * 0.6);
  const c = (mat.pbrMetallicRoughness?.baseColorFactor ?? [1, 1, 1, 1]).slice(0, 3);
  if (!rgba) return c.map(v => v * 0.6);
  let r = 0, g = 0, b = 0, n = 0;
  for (let i = 0; i < rgba.length; i += 4) if (rgba[i + 3] > 128) { r += rgba[i]; g += rgba[i + 1]; b += rgba[i + 2]; n++; }
  const avg = n ? srgbToLinear([r / n, g / n, b / n]) : [0.25, 0.35, 0.18];
  return c.map((v, k) => v * avg[k] * 0.8);
}
