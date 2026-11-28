// Rule 16 per-vertex scan of published tiles: geometry inside each housing outline, by housing, tile and material, with y range.
// Outlines:
//   - every dormitory/residential/apartments place in viewer/places.json as its full circle (r + 2 m);
//   - every ring in blender/scripted/village/v_buildings.json (Hawk Crossings, Fenwick, Williams, Paul, Basie, ...);
//   - the Dinallo and Machuga Heights rings in blender/scripted/northeast/ne_buildings.json (Machuga_dining is Sam's Place, the
//     rule 16 dining-floor exception, reported under its own name);
//   - the housing circles in ws275/housing275.json (adds Webster Hall, tagged university in places.json; scene x, y, r).
// Plain meshes are tested vertex by vertex. Instanced meshes (EXT_mesh_gpu_instancing: trees, lights, chairs) are tested by each
// instance's origin (node transform x instance translation), counted once per instance.
// usage (from /workspace/nj-scenes/web/tools): node house16.mjs <places.json> <v_buildings.json> <ne_buildings.json> <housing275.json> <tiles...>
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import fs from 'fs';
const [places, village, northeast, hous, ...files] = process.argv.slice(2);
const read = f => JSON.parse(fs.readFileSync(f));
const inRing = (x, y, R) => { let c = false; for (let i = 0, j = R.length - 1; i < R.length; j = i++) { const [xa, ya] = R[j], [xb, yb] = R[i]; if ((ya > y) !== (yb > y) && x < (xb - xa) * (y - ya) / (yb - ya) + xa) c = !c; } return c; };
// viewer frame: x = scene x, z = -scene y
const H = read(places).places.filter(p => ['dormitory', 'residential', 'apartments'].includes(p.tags?.building))
  .map(p => ({ name: p.name, has: (x, z) => Math.hypot(x - p.x, z - p.z) < p.r + 2 }))
  .concat(read(village).buildings.map(b => ({ name: b.name, has: (x, z) => inRing(x, -z, b.ring) })))
  .concat(read(northeast).buildings.filter(b => /Dinallo|Machuga/.test(b.name)).map(b => ({ name: b.name, has: (x, z) => inRing(x, -z, b.ring) })))
  .concat(read(hous).map(([name, hx, hy, r]) => ({ name: name + ' (housing275)', has: (x, z) => Math.hypot(x - hx, -z - hy) < r + 2 })));
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const res = new Map();
const add = (k, y) => { const r = res.get(k) || [0, 1e9, -1e9]; r[0]++; r[1] = Math.min(r[1], y); r[2] = Math.max(r[2], y); res.set(k, r); };
const xf = (M, p) => [M[0] * p[0] + M[4] * p[1] + M[8] * p[2] + M[12], M[1] * p[0] + M[5] * p[1] + M[9] * p[2] + M[13], M[2] * p[0] + M[6] * p[1] + M[10] * p[2] + M[14]];
for (const f of files) {
  const doc = await io.read(f); const tile = f.split('/').pop();
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh(); if (!mesh) continue;
    const M = node.getWorldMatrix(); const inst = node.getExtension('EXT_mesh_gpu_instancing');
    const mats = mesh.listPrimitives().map(pr => pr.getMaterial()?.getName() || '');
    if (inst) {
      const T = inst.getAttribute('TRANSLATION'); if (!T) continue;
      const el = [0, 0, 0];
      for (let i = 0; i < T.getCount(); i++) {
        const [x, y, z] = xf(M, T.getElement(i, el));
        for (const h of H) if (h.has(x, z)) for (const m of mats) add(`${h.name}|${tile}|${m} (instance)`, y);
      }
      continue;
    }
    for (const [pi, pr] of mesh.listPrimitives().entries()) {
      const pos = pr.getAttribute('POSITION'); const el = [0, 0, 0];
      for (let i = 0; i < pos.getCount(); i++) {
        const [x, y, z] = xf(M, pos.getElement(i, el));
        for (const h of H) if (h.has(x, z)) add(`${h.name}|${tile}|${mats[pi]}`, y);
      }
    }
  }
}
for (const [k, r] of [...res].sort()) console.log(k, r[0], r[1].toFixed(1), r[2].toFixed(1));
