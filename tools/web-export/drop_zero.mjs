// Drop the triangles of a tile that draw nothing: zero area in the stored (quantized) positions, two corners
// at one place or three on one line (zero.mjs), then the vertices nothing uses any more. When this was written
// 3.98 M of the 22.4 M triangles of models/main were such (2.75 M of the 3.86 M in skirt.glb, 0.22 M in
// context.glb): the viewer downloaded, decoded and ran every one through the vertex shader for nothing.
//   node drop_zero.mjs FILE.glb [FILE.glb ...]
// Lossless: no visible triangle changes. Rewrites a file in place only when it holds such triangles, with the
// same meshopt filters `optimize` wrote; supersede marks and other extras stay on their primitives.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { compactPrimitive, prune } from '@gltf-transform/functions';
import { statSync, writeFileSync } from 'node:fs';
import { keepTriangles } from './zero.mjs';
import { keepShared, sharedRefs } from './tex.mjs';

await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
let saved = 0, total = 0;
for (const f of process.argv.slice(2)) {
  const doc = await io.read(f), root = doc.getRoot(), before = statSync(f).size, { json } = await io.readAsJSON(f);
  const uris = root.listTextures().map(t => t.getURI());
  let dropped = 0;
  for (const mesh of root.listMeshes()) {
    for (const prim of mesh.listPrimitives()) {
      const pos = prim.getAttribute('POSITION'), idx = prim.getIndices();
      if (!pos || !idx || prim.getMode() !== 4) continue;
      const keep = keepTriangles(idx.getArray(), pos.getArray());
      if (!keep) continue;
      dropped += (idx.getCount() - keep.length) / 3;
      if (!keep.length) { prim.dispose(); continue; }
      prim.setIndices(idx.clone().setArray(keep));
      compactPrimitive(prim); // vertices only the dropped triangles used
    }
    if (!mesh.listPrimitives().length) { for (const n of mesh.listParents()) if (n.propertyType === 'Node') n.setMesh(null); mesh.dispose(); }
  }
  if (!dropped) continue;
  await doc.transform(prune({ propertyTypes: ['Accessor'], keepAttributes: true }));
  // write with the method the file has: filtered (optimize) or plain quantized (lod.mjs), so nothing loses precision
  const filtered = (json.bufferViews ?? []).some(v => (v.extensions?.EXT_meshopt_compression?.filter ?? 'NONE') !== 'NONE');
  const { FILTER, QUANTIZE } = EXTMeshoptCompression.EncoderMethod;
  root.listExtensionsUsed().find(e => e.extensionName === 'EXT_meshopt_compression')?.setEncoderOptions({ method: filtered ? FILTER : QUANTIZE });
  writeFileSync(f, keepShared(await io.writeBinary(doc), sharedRefs(uris, f, f)));
  const after = statSync(f).size; saved += before - after; total += dropped;
  console.log(`drop_zero ${f.split('/').pop()}: ${dropped} zero-area triangles, ${(before / 1e6).toFixed(2)} -> ${(after / 1e6).toFixed(2)} MB`);
}
console.log(`drop_zero: ${total} triangles, saved ${(saved / 1e6).toFixed(1)} MB`);
