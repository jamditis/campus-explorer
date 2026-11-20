// Drop vertex data that nothing in a tile uses. `gltf-transform optimize --instance` leaves a second copy of
// every instance's translation, rotation and scale in the file (42.8 MB of raw data across the campus when
// this was written); no mesh or instance refers to it, so the viewer downloads and decodes it for nothing.
//   node compact.mjs FILE.glb [FILE.glb ...]
// It also stores instance rotations as normalized 16-bit integers (pack.mjs): float rotations barely
// compress, and the main model's shrub leaf cards carry hundreds of thousands of them.
// Rewrites a file in place only when it holds such data, with the same meshopt filters `optimize` wrote.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { statSync } from 'node:fs';
import { toNormalizedInt16 } from './pack.mjs';

await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
let saved = 0;
for (const f of process.argv.slice(2)) {
  const doc = await io.read(f), before = statSync(f).size;
  const unused = doc.getRoot().listAccessors().filter(a => !a.listParents().some(p => p.propertyType !== 'Root'));
  const rotations = new Set();
  for (const node of doc.getRoot().listNodes()) {
    const r = node.getExtension('EXT_mesh_gpu_instancing')?.getAttribute('ROTATION');
    if (r && r.getComponentType() === 5126) rotations.add(r); // FLOAT
  }
  if (!unused.length && !rotations.size) continue;
  for (const a of unused) a.dispose();
  for (const r of rotations) r.setArray(toNormalizedInt16(r.getArray())).setNormalized(true);
  doc.getRoot().listExtensionsUsed().find(e => e.extensionName === 'EXT_meshopt_compression')?.setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.FILTER });
  await io.write(f, doc);
  const after = statSync(f).size; saved += before - after;
  console.log(`compact ${f.split('/').pop()}: ${unused.length} unused accessors, ${rotations.size} rotations packed, ${(before / 1e6).toFixed(1)} -> ${(after / 1e6).toFixed(1)} MB`);
}
console.log(`compact: saved ${(saved / 1e6).toFixed(1)} MB`);
