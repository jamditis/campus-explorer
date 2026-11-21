// Drop vertex data that nothing in a tile uses. `gltf-transform optimize --instance` leaves a second copy of
// every instance's translation, rotation and scale in the file (42.8 MB of raw data across the campus when
// this was written); no mesh or instance refers to it, so the viewer downloads and decodes it for nothing.
//   node compact.mjs FILE.glb [FILE.glb ...]
// It also stores instance rotations as normalized 16-bit integers (pack.mjs): float rotations barely
// compress, and the main model's shrub leaf cards carry hundreds of thousands of them.
// And it drops vertex colours that are opaque white at every vertex (pack.mjs isWhite): three.js multiplies the base
// colour by them, so they change nothing, but every such vertex cost 4 bytes of GPU memory and a vertex fetch
// (1.45 M vertices, mostly the main model's shrubs, when this was written).
// Rewrites a file in place only when it holds such data, with the same meshopt filters `optimize` wrote.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { statSync, writeFileSync } from 'node:fs';
import { toNormalizedInt16, isWhite } from './pack.mjs';
import { keepShared, sharedRefs } from './tex.mjs';

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
  const white = [];
  for (const mesh of doc.getRoot().listMeshes()) for (const p of mesh.listPrimitives()) {
    const c = p.getAttribute('COLOR_0');
    if (c && isWhite(c.getArray(), c.getNormalized())) white.push(p);
  }
  if (!unused.length && !rotations.size && !white.length) continue;
  for (const p of white) { const c = p.getAttribute('COLOR_0'); p.setAttribute('COLOR_0', null); if (!c.listParents().some(x => x.propertyType !== 'Root')) c.dispose(); }
  for (const a of unused) a.dispose();
  for (const r of rotations) r.setArray(toNormalizedInt16(r.getArray())).setNormalized(true);
  doc.getRoot().listExtensionsUsed().find(e => e.extensionName === 'EXT_meshopt_compression')?.setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.FILTER });
  // images the tile shares with others (models/main/tex/) stay outside it: io.write would embed them
  const refs = sharedRefs(doc.getRoot().listTextures().map(t => t.getURI()), f, f);
  writeFileSync(f, keepShared(await io.writeBinary(doc), refs));
  const after = statSync(f).size; saved += before - after;
  console.log(`compact ${f.split('/').pop()}: ${unused.length} unused accessors, ${rotations.size} rotations packed, ${white.length} white colours dropped, ${(before / 1e6).toFixed(1)} -> ${(after / 1e6).toFixed(1)} MB`);
}
console.log(`compact: saved ${(saved / 1e6).toFixed(1)} MB`);
