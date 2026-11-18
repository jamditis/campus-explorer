// node tint_leaves.mjs in.glb  -> fixes leaf-card materials in place before optimisation:
//  1. UVs: Blender leaf shaders read a named UV map that the exporter writes as TEXCOORD_1, while
//     TEXCOORD_0 is collapsed to one point (u=0, v=1). Texture lookups then hit one corner texel and the
//     cards draw as pale blobs. Point the leaf textures at the first UV set that actually varies.
//  2. Colour: <in>.glb.leaf.json holds each species' tint from its Blender colour ramp. Scale the
//     factor so the card's average opaque colour lands on a summer-foliage green nudged toward that
//     species hue (authored approximation; Blender's ramp/hue nodes don't exist in glTF).
//  3. Alpha: MASK at 0.5.
import { createRequire } from 'module';
const require = createRequire('/workspace/nj-scenes/web/tools/package.json');
const { NodeIO } = require('@gltf-transform/core'); const { ALL_EXTENSIONS } = require('@gltf-transform/extensions');
const fs = require('fs'); const sharp = require('sharp');
const f = process.argv[2]; const tints = fs.existsSync(f + '.leaf.json') ? JSON.parse(fs.readFileSync(f + '.leaf.json')) : {};
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS); const doc = await io.read(f);
const lin = c => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const avgCache = new Map();
async function opaqueMean(tex) {
  if (avgCache.has(tex)) return avgCache.get(tex);
  const { data, info } = await sharp(Buffer.from(tex.getImage())).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const s = [0, 0, 0]; let n = 0;
  for (let i = 0; i < data.length; i += info.channels * 7) if (data[i + 3] > 127) { for (let k = 0; k < 3; k++) s[k] += lin(data[i + k] / 255); n++; }
  const r = n ? s.map(x => x / n) : [0.2, 0.3, 0.1]; avgCache.set(tex, r); return r;
}
const varies = acc => { const a = acc.getArray(); for (let i = 2; i < a.length; i += 2) if (a[i] !== a[0] || a[i + 1] !== a[1]) return true; return false; };
const GREEN = [0.055, 0.105, 0.03]; const lum = c => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
let n = 0, uvfix = 0;
for (const m of doc.getRoot().listMaterials()) {
  const t = tints[m.getName()]; if (!t) continue;
  const tex = m.getBaseColorTexture();
  // pick the UV set that varies on this material's primitives
  const prims = m.listParents().filter(p => p.propertyType === 'Primitive');
  for (const p of prims) {
    const uv0 = p.getAttribute('TEXCOORD_0'), uv1 = p.getAttribute('TEXCOORD_1');
    if (uv0 && uv1 && !varies(uv0) && varies(uv1)) { p.setAttribute('TEXCOORD_0', uv1); p.setAttribute('TEXCOORD_1', null); uvfix++; }
  }
  let factor = t;
  if (tex) {
    const avg = await opaqueMean(tex);
    const hue = t.map(c => c * lum(GREEN) / Math.max(1e-4, lum(t)));
    const target = GREEN.map((g, i) => g * 0.65 + hue[i] * 0.35);
    factor = target.map((c, i) => Math.min(1, c / Math.max(0.01, avg[i])));
  }
  m.setBaseColorFactor([...factor, 1]); m.setAlphaMode('MASK'); m.setAlphaCutoff(0.5); m.setRoughnessFactor(0.85); m.setMetallicFactor(0); n++;
}
await io.write(f, doc); console.log('tinted', n, 'uv-fixed prims', uvfix, f);
