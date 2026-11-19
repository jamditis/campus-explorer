// Dump the triangles of published tiles that touch a box, in the model frame (x east, y north, z up),
// so a script can draw a plan of what the viewer already has there (tools/evidence/plan.py).
//   node tools/evidence/dump_tiles.mjs OUT_DIR X0 Y0 X1 Y1 [models/main]
// Writes OUT_DIR/tiles.json (one entry per mesh primitive: tile, mesh, material, colour, category, offsets)
// and OUT_DIR/tiles.bin (float32 triangle corners, 9 numbers per triangle). Instanced meshes are expanded.
// Needs @gltf-transform/core, @gltf-transform/extensions and meshoptimizer (not vendored: use NODE_PATH).
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import { readdirSync, writeFileSync, mkdirSync } from 'node:fs';

const [out, X0, Y0, X1, Y1, dir = 'models/main'] = process.argv.slice(2);
const [x0, y0, x1, y1] = [X0, Y0, X1, Y1].map(Number);
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const TILE = 160, entries = [], chunks = [];
let offset = 0;
const touches = f => {
  const m = /^(?:n_)?t_(-?\d+)_(-?\d+)\.glb$/.exec(f);
  if (!m) return true; // context, skirt, far houses: no tile grid
  // objects are filed under the tile that holds their centre and can reach well past it: take a wide margin
  // (the per-triangle test below keeps only what is in the box)
  const tx = +m[1] * TILE, ty = +m[2] * TILE, pad = 350;
  return tx - pad < x1 && tx + TILE + pad > x0 && ty - pad < y1 && ty + TILE + pad > y0;
};
const mul = (m, p) => [m[0] * p[0] + m[4] * p[1] + m[8] * p[2] + m[12], m[1] * p[0] + m[5] * p[1] + m[9] * p[2] + m[13], m[2] * p[0] + m[6] * p[1] + m[10] * p[2] + m[14]];
const compose = (a, b) => { const o = new Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3]; return o; };
const trs = (t, q, s) => {
  const [x, y, z, w] = q, [sx, sy, sz] = s;
  return [(1 - 2 * (y * y + z * z)) * sx, 2 * (x * y + z * w) * sx, 2 * (x * z - y * w) * sx, 0, 2 * (x * y - z * w) * sy, (1 - 2 * (x * x + z * z)) * sy, 2 * (y * z + x * w) * sy, 0,
    2 * (x * z + y * w) * sz, 2 * (y * z - x * w) * sz, (1 - 2 * (x * x + y * y)) * sz, 0, t[0], t[1], t[2], 1];
};
for (const f of readdirSync(dir).filter(f => f.endsWith('.glb') && touches(f)).sort()) {
  const doc = await io.read(`${dir}/${f}`);
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh(); if (!mesh) continue;
    const world = node.getWorldMatrix(), inst = node.getExtension('EXT_mesh_gpu_instancing');
    const mats = [];
    if (inst) {
      const T = inst.getAttribute('TRANSLATION'), R = inst.getAttribute('ROTATION'), S = inst.getAttribute('SCALE');
      for (let i = 0; i < T.getCount(); i++) mats.push(compose(world, trs(T.getElement(i, []), R ? R.getElement(i, []) : [0, 0, 0, 1], S ? S.getElement(i, []) : [1, 1, 1])));
    } else mats.push(world);
    for (const prim of mesh.listPrimitives()) {
      const pos = prim.getAttribute('POSITION'), idx = prim.getIndices(); if (!pos || prim.getMode() !== 4) continue;
      const n = idx ? idx.getCount() : pos.getCount(), local = [], p = [];
      for (let i = 0; i < pos.getCount(); i++) local.push(pos.getElement(i, []));
      const tri = [];
      for (const m of mats) {
        const w = local.map(v => mul(m, v)); // viewer axes: x east, y up, z south
        for (let i = 0; i < n; i += 3) {
          const a = w[idx ? idx.getScalar(i) : i], b = w[idx ? idx.getScalar(i + 1) : i + 1], c = w[idx ? idx.getScalar(i + 2) : i + 2];
          const minx = Math.min(a[0], b[0], c[0]), maxx = Math.max(a[0], b[0], c[0]), miny = -Math.max(a[2], b[2], c[2]), maxy = -Math.min(a[2], b[2], c[2]);
          if (maxx < x0 || minx > x1 || maxy < y0 || miny > y1) continue;
          tri.push(a[0], -a[2], a[1], b[0], -b[2], b[1], c[0], -c[2], c[1]);
        }
      }
      if (!tri.length) continue;
      const mat = prim.getMaterial();
      entries.push({ tile: f, mesh: mesh.getName(), node: node.getName(), material: mat?.getName() ?? '', color: mat?.getBaseColorFactor() ?? [1, 1, 1, 1],
        cat: mat?.getExtras()?.cat ?? '', alpha: mat?.getAlphaMode() ?? 'OPAQUE', instanced: !!inst, offset, tris: tri.length / 9 });
      chunks.push(new Float32Array(tri)); offset += tri.length / 9;
    }
  }
  console.log(f, entries.length, 'primitives so far');
}
mkdirSync(out, { recursive: true });
const all = new Float32Array(offset * 9); let at = 0;
for (const c of chunks) { all.set(c, at); at += c.length; }
writeFileSync(`${out}/tiles.bin`, Buffer.from(all.buffer));
writeFileSync(`${out}/tiles.json`, JSON.stringify({ box: [x0, y0, x1, y1], entries }));
console.log('wrote', offset, 'triangles from', entries.length, 'primitives');
