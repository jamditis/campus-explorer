// Rule 16 per-vertex scan of published tiles: vertices inside housing circles (0.85 r), by housing, tile and material, with y range.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import fs from 'fs';
const [places, ...files] = process.argv.slice(2);
const H = JSON.parse(fs.readFileSync(places)).places.filter(p => ['dormitory', 'residential', 'apartments'].includes(p.tags?.building));
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const res = new Map();
for (const f of files) {
  const doc = await io.read(f);
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh(); if (!mesh) continue;
    const M = node.getWorldMatrix();
    const inst = node.getExtension('EXT_mesh_gpu_instancing');
    if (inst) continue; // instanced props (trees, lights): not interiors
    for (const pr of mesh.listPrimitives()) {
      const pos = pr.getAttribute('POSITION'); const mat = pr.getMaterial()?.getName() || '';
      const el = [0, 0, 0];
      for (let i = 0; i < pos.getCount(); i++) {
        pos.getElement(i, el);
        const x = M[0] * el[0] + M[4] * el[1] + M[8] * el[2] + M[12], y = M[1] * el[0] + M[5] * el[1] + M[9] * el[2] + M[13], z = M[2] * el[0] + M[6] * el[1] + M[10] * el[2] + M[14];
        for (const h of H) if (Math.hypot(x - h.x, z - h.z) < 0.85 * h.r) {
          const k = `${h.name}|${f.split('/').pop()}|${mat}`; const r = res.get(k) || [0, 1e9, -1e9];
          r[0]++; r[1] = Math.min(r[1], y); r[2] = Math.max(r[2], y); res.set(k, r);
        }
      }
    }
  }
}
for (const [k, r] of [...res].sort()) console.log(k, r[0], r[1].toFixed(1), r[2].toFixed(1));
