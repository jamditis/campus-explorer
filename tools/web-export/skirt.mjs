// Lighter far-field ground: simplify the 4 km skirt (Context_skirt_*) to within ERR_M metres (default 0.05) of
// its exported surface. Its ring next to the campus is a 0.34 m mesh of 1 m LiDAR ground; 5 cm is under a
// pixel from 50 m away and under the LiDAR's own vertical error. Borders (the campus edge, cuts, material seams)
// stay exactly where they are, and only existing vertices are kept, so heights at those vertices do not move.
//   node skirt.mjs FILE.glb [FILE.glb ...]
// A primitive is marked in its extras (`simplified`: the error used), so a second run leaves it alone and the
// error never adds up. Rewrites a file only when something changed, with the meshopt method the file has.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { MeshoptEncoder, MeshoptDecoder, MeshoptSimplifier } from 'meshoptimizer';
import { compactPrimitive, prune } from '@gltf-transform/functions';
import { statSync, writeFileSync } from 'node:fs';
import { keepShared, sharedRefs } from './tex.mjs';

const ERR_M = +(process.env.ERR_M || 0.05), NAME = /^Context_skirt/;
await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready, MeshoptSimplifier.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
for (const f of process.argv.slice(2)) {
  const doc = await io.read(f), root = doc.getRoot(), before = statSync(f).size, { json } = await io.readAsJSON(f);
  const uris = root.listTextures().map(t => t.getURI());
  let was = 0, now = 0;
  for (const node of root.listNodes()) {
    const mesh = node.getMesh();
    if (!mesh || !NAME.test(node.getName()) || node.getExtension('EXT_mesh_gpu_instancing')) continue;
    const W = node.getWorldMatrix();
    for (const prim of mesh.listPrimitives()) {
      const pos = prim.getAttribute('POSITION'), idx = prim.getIndices();
      if (!pos || !idx || prim.getMode() !== 4 || prim.getExtras().simplified) continue;
      // world positions (the node's scale and offset undo the quantization), so the error is in metres
      const n = pos.getCount(), P = new Float32Array(n * 3), el = [];
      for (let i = 0; i < n; i++) {
        pos.getElement(i, el);
        for (let k = 0; k < 3; k++) P[i * 3 + k] = W[k] * el[0] + W[4 + k] * el[1] + W[8 + k] * el[2] + W[12 + k];
      }
      const I = new Uint32Array(idx.getArray());
      const [J] = MeshoptSimplifier.simplify(I, P, 3, 0, ERR_M, ['ErrorAbsolute', 'LockBorder']);
      was += I.length / 3; now += J.length / 3;
      prim.setExtras({ ...prim.getExtras(), simplified: ERR_M });
      if (J.length === I.length) continue;
      prim.setIndices(idx.clone().setArray(n > 65535 ? J : new Uint16Array(J)));
      compactPrimitive(prim);
    }
  }
  if (!was) { console.log(`skirt ${f.split('/').pop()}: nothing to simplify`); continue; }
  await doc.transform(prune({ propertyTypes: ['Accessor'], keepAttributes: true }));
  const filtered = (json.bufferViews ?? []).some(v => (v.extensions?.EXT_meshopt_compression?.filter ?? 'NONE') !== 'NONE');
  const { FILTER, QUANTIZE } = EXTMeshoptCompression.EncoderMethod;
  root.listExtensionsUsed().find(e => e.extensionName === 'EXT_meshopt_compression')?.setEncoderOptions({ method: filtered ? FILTER : QUANTIZE });
  writeFileSync(f, keepShared(await io.writeBinary(doc), sharedRefs(uris, f, f)));
  console.log(`skirt ${f.split('/').pop()}: ${was} -> ${now} triangles within ${ERR_M} m, ${(before / 1e6).toFixed(2)} -> ${(statSync(f).size / 1e6).toFixed(2)} MB`);
}
