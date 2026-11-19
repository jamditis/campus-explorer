// Far-distance version of a campus tile: drops instanced nodes (trees, repeated assets: the viewer keeps the full
// tile's instances) and meshes smaller than MIN m, then simplifies what is left. usage: node lod.mjs in.glb out.glb
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { weld, prune, dedup, meshopt, getBounds, compactPrimitive, dequantize, quantize } from '@gltf-transform/functions';
import { MeshoptSimplifier, MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
const [inp, out] = process.argv.slice(2);
const MIN = +(process.env.MIN || 6), RATIO = +(process.env.RATIO || 0.25), ERR_M = +(process.env.ERR_M || 0.4); // error in metres
await Promise.all([MeshoptSimplifier.ready, MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
const doc = await io.read(inp);
const root = doc.getRoot();
let dropped = 0;
for (const node of root.listNodes()) {
  const mesh = node.getMesh(); if (!mesh) continue;
  const inst = node.getExtension('EXT_mesh_gpu_instancing');
  if (inst) { node.setMesh(null); node.setExtension('EXT_mesh_gpu_instancing', null); for (const a of inst.listAttributes()) a.dispose(); inst.dispose(); dropped++; continue; }
  const b = getBounds(node); const d = Math.hypot(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]);
  if (d < MIN) { node.setMesh(null); dropped++; }
}
for (const m of root.listMaterials()) if (m.getAlphaMode() === 'BLEND') for (const n of root.listNodes()) if (n.getMesh()?.listPrimitives().some(p => p.getMaterial() === m)) n.setMesh(null);
await doc.transform(prune(), dedup(), dequantize(), weld());
// sloppy simplification: collapses across disconnected parts (tile courses, mullions) that topology-preserving
// simplification can't touch; the error bound is in metres, sized for viewing from a few hundred metres away
let before = 0, after = 0;
for (const mesh of root.listMeshes()) for (const prim of mesh.listPrimitives()) {
  const idx = prim.getIndices(), pos = prim.getAttribute('POSITION'); if (!idx || !pos || prim.getMode() !== 4) continue;
  const P = new Float32Array(pos.getArray()), I = new Uint32Array(idx.getArray());
  const scale = MeshoptSimplifier.getScale(P, 3) || 1;
  const [J] = MeshoptSimplifier.simplifySloppy(I, P, 3, null, Math.max(3, Math.floor(I.length * RATIO / 3) * 3), ERR_M / scale);
  before += I.length / 3; after += J.length / 3;
  if (J.length < 3) { prim.dispose(); continue; }
  idx.setArray(J); compactPrimitive(prim);
}
for (const mesh of root.listMeshes()) if (!mesh.listPrimitives().length) mesh.dispose();
await doc.transform(prune(), quantize(), meshopt({ encoder: MeshoptEncoder, level: 'medium' }));
console.log('tris', before, '->', after);
await io.write(out, doc);
console.log('lod', inp.split('/').pop(), 'dropped nodes', dropped);
