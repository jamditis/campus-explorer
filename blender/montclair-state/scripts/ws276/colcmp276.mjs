// ws276 colcmp276 (run from /workspace/nj-scenes/web/tools): flattened colour per material (name without .00N) of a published tile and its re-export; prints every material whose colour, texture or emission differs. Run before publishing any tile exported from a release-derived file.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
async function cols(f) {
  const m = new Map();
  for (const x of (await io.read(f)).getRoot().listMaterials()) {
    const k = x.getName().replace(/\.\d{3}$/, '');
    m.set(k, { c: x.getBaseColorFactor().map(v => +v.toFixed(3)).join(','), t: !!x.getBaseColorTexture(), e: x.getEmissiveFactor().map(v => +v.toFixed(2)).join(','), raw: x.getName() });
  }
  return m;
}
const a = await cols(process.argv[2]), b = await cols(process.argv[3]);
let same = 0;
for (const [k, v] of a) { const w = b.get(k); if (!w) { console.log('GONE', k); continue; } if (v.c !== w.c || v.t !== w.t || v.e !== w.e) console.log('DIFF', k, v.raw, v.c, v.t, '->', w.raw, w.c, w.t); else same++; }
for (const k of b.keys()) if (!a.has(k)) console.log('NEW', k);
console.log('same', same);
