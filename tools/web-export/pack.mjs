// Pure helpers for the tile scripts (compact.mjs, lod.mjs); no dependencies, unit-tested from node --test.
// build_web.sh copies this file next to those scripts before it runs them.

/**
 * Unit values (instance rotation quaternions) as normalized signed 16-bit integers, which
 * EXT_mesh_gpu_instancing allows for ROTATION: 8 bytes an instance instead of 16, and an angle
 * error under 1e-4 rad. Float rotations barely compress, so this is most of what they cost.
 */
export function toNormalizedInt16(values) {
  const out = new Int16Array(values.length);
  for (let i = 0; i < values.length; i++) out[i] = Math.round(Math.max(-1, Math.min(1, values[i])) * 32767);
  return out;
}

/**
 * Image size in a far version (lod/): half the full tile's size per side. The far version shows from
 * 260 m at the nearest, where a screen pixel covers more ground than a texel of the half-size image;
 * the GPU would sample the smaller mip levels there anyway. Images of 64 px or less stay as they are.
 */
export function farImageSize([w, h]) {
  if (Math.max(w, h) <= 64) return [w, h];
  return [Math.max(1, Math.round(w / 2)), Math.max(1, Math.round(h / 2))];
}

/**
 * Tree meshes: the shared `Tree_*` meshes the Blender files link into every tree object (main, north and
 * scripted alike). Shrubs are not trees here, as in the viewer's trees.js.
 */
export function isTreeMesh(name) {
  return typeof name === 'string' && name.startsWith('Tree_') && !/shrub/i.test(name);
}

/**
 * Which nodes tree_instance.mjs turns into one GPU instance batch each, before `optimize`. `nodes` is
 * one entry per node: { mesh (any key, compared by identity; null for none), name (the mesh's name),
 * skin, instanced }. A tree mesh used by `min` or more plain nodes gives one batch: the list of those
 * node indices. Other meshes are left to `optimize`, which instances only at 5 or more and joins the
 * rest: joined fixtures keep their collision. A mesh with a skinned node is skipped, as instance() does.
 */
export function treeBatches(nodes, min = 2) {
  const byMesh = new Map();
  nodes.forEach((n, i) => {
    if (n.mesh == null || n.instanced || !isTreeMesh(n.name)) return;
    if (!byMesh.has(n.mesh)) byMesh.set(n.mesh, []);
    byMesh.get(n.mesh).push(i);
  });
  return [...byMesh.values()].filter(ix => ix.length >= min && !ix.some(i => nodes[i].skin));
}

/**
 * The 3x3 linear part of an instance matrix, column-major, as three.js Matrix4.compose builds it (GLTFLoader's
 * path for EXT_mesh_gpu_instancing). A quaternion a little off unit length gives a slightly sheared matrix.
 */
export function linearPart([x, y, z, w], [sx, sy, sz]) {
  const x2 = x + x, y2 = y + y, z2 = z + z;
  const xx = x * x2, xy = x * y2, xz = x * z2, yy = y * y2, yz = y * z2, zz = z * z2, wx = w * x2, wy = w * y2, wz = w * z2;
  return [(1 - (yy + zz)) * sx, (xy + wz) * sx, (xz - wy) * sx, (xy - wz) * sy, (1 - (xx + zz)) * sy, (yz + wx) * sy,
    (xz + wy) * sz, (yz - wx) * sz, (1 - (xx + yy)) * sz];
}

/**
 * How far any vertex within `radius` of the mesh origin can move when instance `a` ({ t, q, s }) is stored as `b`:
 * the move of the origin plus the Frobenius norm of the change in the linear part (an upper bound of how much it
 * stretches a vector) times the radius.
 */
export function instanceShift(a, b, radius) {
  const la = linearPart(a.q, a.s), lb = linearPart(b.q, b.s);
  let f = 0; for (let i = 0; i < 9; i++) f += (la[i] - lb[i]) ** 2;
  return Math.hypot(a.t[0] - b.t[0], a.t[1] - b.t[1], a.t[2] - b.t[2]) + Math.sqrt(f) * radius;
}

/** Quaternions (x, y, z, w per instance) scaled to unit length, as Float32Array; a zero one becomes no turn. */
export function unitQuats(values) {
  const out = new Float32Array(values.length);
  for (let i = 0; i < values.length; i += 4) {
    const l = Math.hypot(values[i], values[i + 1], values[i + 2], values[i + 3]);
    if (!l) { out[i + 3] = 1; continue; }
    for (let j = 0; j < 4; j++) out[i + j] = values[i + j] / l;
  }
  return out;
}

/** Normalized integers (glTF `normalized: true`) to floats, as the glTF spec decodes them; floats pass through. */
export function decodeUnit(values) {
  const max = { Int8Array: 127, Uint8Array: 255, Int16Array: 32767, Uint16Array: 65535 }[values.constructor.name];
  if (!max) return Float32Array.from(values);
  const signed = values instanceof Int8Array || values instanceof Int16Array, out = new Float32Array(values.length);
  for (let i = 0; i < values.length; i++) out[i] = signed ? Math.max(values[i] / max, -1) : values[i] / max;
  return out;
}

/** The first of `candidates` (bit counts, fewest first) whose error `err(bits)` is within `tol`, else null. */
export function fewestBits(candidates, err, tol) {
  for (const b of candidates) if (err(b) <= tol) return b;
  return null;
}

/**
 * True when a COLOR_0 array is opaque white at every vertex (all components at 1 once decoded): three.js multiplies
 * the base colour by it, so it changes nothing and only costs a vertex attribute. Empty arrays are not white.
 */
export function isWhite(values, normalized) {
  if (!values.length) return false;
  const one = !normalized || values instanceof Float32Array ? 1 : { Uint8Array: 255, Uint16Array: 65535 }[values.constructor.name];
  if (!one) return false;
  for (let i = 0; i < values.length; i++) if (values[i] !== one) return false;
  return true;
}

/**
 * Whether a far version (lod.mjs) is worth shipping. `full` and `far`: { tris, draws } of the plain (not instanced)
 * meshes. One that keeps `keep` (80 %) or more of both the triangles and the draw calls is nearly a copy: the viewer
 * would download it and hold both in GPU memory for almost no saving at distance. An empty one draws nothing.
 */
export function farWorthIt(full, far, keep = 0.8) {
  if (!far.tris) return false;
  return far.tris < keep * full.tris || far.draws < keep * full.draws;
}

/**
 * Put back the pieces that simplifying cut down: a far version must keep the skyline. Simplifying to half a metre
 * collapses a part narrower than that, so a TV mast lost its top 21.6 m, goalposts 6 m and a pavilion 15 m.
 * A piece is a connected part of the mesh (vertices joined where they meet, so hard edges do not split it). One
 * at least `tall` metres high (world y)
 * whose top in `J` (the simplified triangles) is `drop` metres or more below its top in `I` (or gone) gets all its
 * own triangles back, in place of what was left of it. P: positions (xyz), m: world matrix (16, column-major).
 * Returns the triangle indices and how many pieces came back.
 */
export function keepSkyline(P, I, J, m, tall = 4, drop = 1) {
  const n = P.length / 3, parent = new Int32Array(n).map((_, i) => i);
  const find = i => { while (parent[i] !== i) i = parent[i] = parent[parent[i]]; return i; };
  // vertices at the same place join (to the millimetre): a hard edge or a UV seam splits vertices but not a piece
  const at = new Map();
  for (let v = 0; v < n; v++) {
    const k = `${Math.round(P[v * 3] * 1000)},${Math.round(P[v * 3 + 1] * 1000)},${Math.round(P[v * 3 + 2] * 1000)}`;
    if (at.has(k)) parent[find(v)] = find(at.get(k)); else at.set(k, v);
  }
  for (let t = 0; t < I.length; t += 3) { const a = find(I[t]); parent[find(I[t + 1])] = a; parent[find(I[t + 2])] = a; }
  const y = new Float64Array(n);
  for (let v = 0; v < n; v++) y[v] = m[1] * P[v * 3] + m[5] * P[v * 3 + 1] + m[9] * P[v * 3 + 2] + m[13];
  const top = new Map(), low = new Map(), kept = new Map();
  for (const v of I) { const r = find(v); top.set(r, Math.max(top.get(r) ?? -Infinity, y[v])); low.set(r, Math.min(low.get(r) ?? Infinity, y[v])); }
  for (const v of J) { const r = find(v); kept.set(r, Math.max(kept.get(r) ?? -Infinity, y[v])); }
  const back = new Set();
  for (const [r, t] of top) if (t - low.get(r) >= tall && t - (kept.get(r) ?? -Infinity) >= drop) back.add(r);
  if (!back.size) return { indices: J, restored: 0 };
  const out = [];
  for (let t = 0; t < J.length; t += 3) if (!back.has(find(J[t]))) out.push(J[t], J[t + 1], J[t + 2]);
  for (let t = 0; t < I.length; t += 3) if (back.has(find(I[t]))) out.push(I[t], I[t + 1], I[t + 2]);
  return { indices: Uint32Array.from(out), restored: back.size };
}
