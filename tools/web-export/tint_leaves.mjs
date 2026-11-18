// node tint_leaves.mjs in.glb  -> applies <in>.glb.leaf.json tints to leaf materials' baseColorFactor (in place)
import { createRequire } from 'module';
const require = createRequire('/workspace/nj-scenes/web/tools/package.json');
const { NodeIO } = require('@gltf-transform/core'); const { ALL_EXTENSIONS } = require('@gltf-transform/extensions');
const fs = require('fs');
const f = process.argv[2]; const tints = fs.existsSync(f + '.leaf.json') ? JSON.parse(fs.readFileSync(f + '.leaf.json')) : {};
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS); const doc = await io.read(f); let n = 0;
for (const m of doc.getRoot().listMaterials()) { const t = tints[m.getName()]; if (t) { m.setBaseColorFactor([...t, 1]); m.setAlphaMode('MASK'); m.setAlphaCutoff(0.5); n++; } }
await io.write(f, doc); console.log('tinted', n, f);
