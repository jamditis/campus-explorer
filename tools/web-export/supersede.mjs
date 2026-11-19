// One campus, several sources: where the southwest build owns the ground, take the other sources' ground
// out of their tiles, so two grounds never lie on top of each other. Rules come from
// blender/southwest/supersede.py (footprint outline, and which meshes are ground there).
//   node supersede.mjs RULES.json MODELS_DIR
// For every tile that is not a southwest tile:
//   clip  meshes: triangles wholly inside the footprint are removed; a kept triangle that reaches into it has
//         those corners lowered by `tuck` metres, so the old ground dips under the new ground's edge
//   drop  meshes: triangles wholly inside the footprint are removed, nothing else changes
// Far-field trees (far_trees.bin) inside the footprint are removed too: they are a scatter, not real trees.
// A primitive is marked in its extras once done, so a second run leaves it alone. Geometry stays in its
// quantized form and is written back with the same meshopt filters, so a tile does not grow or lose precision.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { compactPrimitive } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';

const [rulesFile, dir] = process.argv.slice(2);
if (!rulesFile || !dir) { console.error('usage: node supersede.mjs RULES.json MODELS_DIR'); process.exit(2); }
const rules = JSON.parse(readFileSync(rulesFile, 'utf8'));
const ring = rules.footprint, TUCK = rules.tuck ?? 0.5, TILE = 160;
const CLIP = rules.clip.map(r => new RegExp(r)), DROP = rules.drop.map(r => new RegExp(r));
const bx = [Math.min(...ring.map(p => p[0])), Math.min(...ring.map(p => p[1])), Math.max(...ring.map(p => p[0])), Math.max(...ring.map(p => p[1]))];
/** Even-odd test in the model frame (x east, y north). */
function inside(ring, x, y) {
  let hit = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const a = ring[i], b = ring[j];
    if ((a[1] > y) !== (b[1] > y) && x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])) hit = !hit;
  }
  return hit;
}
const within = (x, y) => x >= bx[0] && x <= bx[2] && y >= bx[1] && y <= bx[3] && inside(ring, x, y);
const touches = f => {
  const m = /^(?:n_)?t_(-?\d+)_(-?\d+)\.glb$/.exec(f);
  if (!m) return true; // context, skirt, far houses
  const tx = +m[1] * TILE, ty = +m[2] * TILE, pad = 200; // objects are filed by their centre and can reach past the tile
  return tx - pad < bx[2] && tx + TILE + pad > bx[0] && ty - pad < bx[3] && ty + TILE + pad > bx[1];
};

await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
const changedTiles = [];
for (const f of readdirSync(dir).filter(f => f.endsWith('.glb') && !f.startsWith('sw_') && touches(f)).sort()) {
  const doc = await io.read(`${dir}/${f}`);
  let removed = 0, tucked = 0, removedAll = 0;
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh();
    if (!mesh || node.getExtension('EXT_mesh_gpu_instancing')) continue;
    const w = node.getWorldMatrix();
    // lowering by TUCK along world up (viewer +Y), written in the mesh's own space: inverse(rotation * scale) * (0, -TUCK, 0)
    const s2 = k => (w[k] * w[k] + w[k + 1] * w[k + 1] + w[k + 2] * w[k + 2]) || 1;
    const down = [-TUCK * w[1] / s2(0), -TUCK * w[5] / s2(4), -TUCK * w[9] / s2(8)];
    for (const prim of mesh.listPrimitives()) {
      const label = `${mesh.getName()} ${prim.getMaterial()?.getName() ?? ''}`;
      const mode = DROP.some(r => r.test(label)) ? 'drop' : CLIP.some(r => r.test(label)) ? 'clip' : null;
      if (!mode || prim.getMode() !== 4 || prim.getExtras().superseded) continue;
      const src = prim.getAttribute('POSITION'), idx = prim.getIndices();
      if (!src || !idx) continue;
      const n = src.getCount(), isIn = new Uint8Array(n), p = [0, 0, 0];
      let any = false;
      for (let i = 0; i < n; i++) {
        src.getElement(i, p);
        const x = w[0] * p[0] + w[4] * p[1] + w[8] * p[2] + w[12], z = w[2] * p[0] + w[6] * p[1] + w[10] * p[2] + w[14];
        if (within(x, -z)) { isIn[i] = 1; any = true; } // viewer z is minus model y
      }
      if (!any) continue;
      const I = idx.getArray(), keep = [], lower = new Uint8Array(n);
      for (let t = 0; t < I.length; t += 3) {
        const a = I[t], b = I[t + 1], c = I[t + 2];
        if (isIn[a] && isIn[b] && isIn[c]) { removed++; continue; }
        keep.push(a, b, c);
        if (mode === 'clip') { if (isIn[a]) lower[a] = 1; if (isIn[b]) lower[b] = 1; if (isIn[c]) lower[c] = 1; }
      }
      if (!keep.length) { mesh.removePrimitive(prim); prim.dispose(); removedAll++; continue; }
      // accessors can be shared between primitives: edit copies, and drop the originals nobody uses any more
      const pos = src.clone(); prim.setAttribute('POSITION', pos);
      const q = [0, 0, 0];
      for (let i = 0; i < n; i++) {
        if (!lower[i]) continue;
        pos.getElement(i, p); pos.setElement(i, [p[0] + down[0], p[1] + down[1], p[2] + down[2]]); pos.getElement(i, q);
        // positions are quantized to the mesh's own box: a corner already at the bottom of it cannot go lower
        if (Math.abs(q[1] - p[1] - down[1]) > Math.abs(down[1]) * 0.2) pos.setElement(i, p); else tucked++;
      }
      prim.setIndices(idx.clone().setArray(n > 65535 ? new Uint32Array(keep) : new Uint16Array(keep)));
      for (const old of [src, idx]) if (!old.listParents().some(x => x.propertyType !== 'Root')) old.dispose();
      compactPrimitive(prim); // drops the corners no triangle uses any more; the index buffer compresses badly with gaps
      prim.setExtras({ ...prim.getExtras(), superseded: true });
    }
    if (!mesh.listPrimitives().length) node.setMesh(null);
  }
  if (!removed && !tucked) continue;
  for (const m of doc.getRoot().listMeshes()) if (!m.listPrimitives().length) m.dispose();
  for (const a of doc.getRoot().listAccessors()) if (!a.listParents().some(x => x.propertyType !== 'Root')) a.dispose();
  // same encoding as `gltf-transform optimize --compress meshopt` wrote
  doc.getRoot().listExtensionsUsed().find(e => e.extensionName === 'EXT_meshopt_compression')?.setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.FILTER });
  await io.write(`${dir}/${f}`, doc);
  changedTiles.push(f);
  console.log(`supersede ${f}: removed ${removed} triangles (${removedAll} whole primitives), tucked ${tucked} corners`);
}
// far-field trees: [x, y, z, crown radius, height] in viewer axes
const ft = `${dir}/far_trees.bin`;
if (existsSync(ft)) {
  const a = new Float32Array(readFileSync(ft).buffer.slice(0)), keep = [];
  for (let i = 0; i + 4 < a.length; i += 5) if (!within(a[i], -a[i + 2])) keep.push(a[i], a[i + 1], a[i + 2], a[i + 3], a[i + 4]);
  if (keep.length !== a.length) { writeFileSync(ft, Buffer.from(new Float32Array(keep).buffer)); console.log(`supersede far_trees.bin: removed ${(a.length - keep.length) / 5} trees`); }
}
// the caller rebuilds the far versions (lod/) of these tiles
console.log('CHANGED', changedTiles.join(' '));
