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
