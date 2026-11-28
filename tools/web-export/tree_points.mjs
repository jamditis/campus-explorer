// Stand-ins for the instanced trees of every tile, written into its far version as scene extras `trees`
// (STAND_IN floats per tree, viewer/trees-math.js). Far versions carry no instances (lod.mjs), and trees.js builds
// its tree stand-ins from full tiles, so under the lite profile's memory budget a tile shown by its far version had
// no instanced trees: this gives the viewer their crowns and trunks without the full tile (scenery.js prepare).
//   node tree_points.mjs DIR    (DIR = models/main; rewrites lod/<tile>.glb only where `trees` changed)
// Reads the published files as they are (shared images in tex/, geometry in geo/), so build_web.sh runs it last,
// after share_geo.mjs and before manifest.py; a second run changes nothing.
import { readFileSync, writeFileSync, readdirSync, existsSync, renameSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { MeshoptDecoder } from 'meshoptimizer';
import sharp from 'sharp';
import { parseGlb, buildGlb } from './tex.mjs';
import { decodeUnit } from './pack.mjs';
import { mul, compose, treeGroups, record, leafColour } from './treepoints.mjs';

await MeshoptDecoder.ready;
const MESHOPT = 'EXT_meshopt_compression', INST = 'EXT_mesh_gpu_instancing';
const TYPED = { 5120: Int8Array, 5121: Uint8Array, 5122: Int16Array, 5123: Uint16Array, 5125: Uint32Array, 5126: Float32Array };
const SIZE = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 };
const TILE = /^(n_|sw_)?t_-?\d+_-?\d+\.glb$/;

function reader(file) {
  const { json, bin } = parseGlb(readFileSync(file)), cache = new Map();
  const buffer = i => {
    if (!cache.has(i)) cache.set(i, json.buffers[i].uri ? new Uint8Array(readFileSync(join(dirname(file), decodeURIComponent(json.buffers[i].uri)))) : bin);
    return cache.get(i);
  };
  const view = vi => {
    const v = json.bufferViews[vi], m = v.extensions?.[MESHOPT];
    if (!m) { const b = buffer(v.buffer), o = v.byteOffset || 0; return { u8: b.subarray(o, o + v.byteLength), stride: v.byteStride }; }
    const out = new Uint8Array(m.count * m.byteStride), b = buffer(m.buffer), o = m.byteOffset || 0;
    MeshoptDecoder.decodeGltfBuffer(out, m.count, m.byteStride, b.subarray(o, o + m.byteLength), m.mode, m.filter);
    return { u8: out, stride: m.byteStride };
  };
  // an accessor's elements as floats, normalized integers mapped to -1..1 or 0..1
  const accessor = ai => {
    const a = json.accessors[ai], n = SIZE[a.type], T = TYPED[a.componentType], { u8, stride } = view(a.bufferView);
    const size = T.BYTES_PER_ELEMENT * n, step = stride || size, el = new T(a.count * n), to = new Uint8Array(el.buffer);
    for (let i = 0; i < a.count; i++) { const o = (a.byteOffset || 0) + i * step; to.set(u8.subarray(o, o + size), i * size); }
    return a.normalized ? decodeUnit(el) : Float32Array.from(el);
  };
  const image = ii => {
    const im = json.images[ii];
    if (im.uri) return readFileSync(join(dirname(file), decodeURIComponent(im.uri)));
    const { u8 } = view(im.bufferView); return Buffer.from(u8);
  };
  return { json, bin, accessor, image };
}

// box of a primitive's positions in its own space: accessor min/max (normalized values mapped like the data)
function box(r, ai) {
  const a = r.json.accessors[ai];
  if (a.min && a.max && !a.normalized) return { min: a.min.slice(0, 3), max: a.max.slice(0, 3) };
  const p = r.accessor(ai), min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < p.length; i += 3) for (let k = 0; k < 3; k++) { min[k] = Math.min(min[k], p[i + k]); max[k] = Math.max(max[k], p[i + k]); }
  return { min, max };
}
const union = boxes => ({ min: [0, 1, 2].map(k => Math.min(...boxes.map(b => b.min[k]))), max: [0, 1, 2].map(k => Math.max(...boxes.map(b => b.max[k]))) });

async function standIns(file) {
  const r = reader(file), { json } = r, nodes = [], world = new Map();
  const walk = (i, parent, pm) => {
    const n = json.nodes[i], m = mul(pm, n.matrix ?? compose(n.translation, n.rotation, n.scale));
    world.set(i, m);
    const ext = n.extensions?.[INST];
    if (ext && n.mesh !== undefined) {
      const mesh = json.meshes[n.mesh];
      nodes.push({
        node: i, parent, count: json.accessors[Object.values(ext.attributes)[0]].count, name: n.name ?? mesh.name,
        prims: mesh.primitives.map(p => ({ material: json.materials?.[p.material] ?? {}, name: mesh.name, position: p.attributes.POSITION })),
      });
    }
    for (const c of n.children ?? []) walk(c, i, m);
  };
  for (const i of json.scenes[json.scene ?? 0].nodes) walk(i, -1, compose());
  const out = [];
  for (const g of treeGroups(nodes)) {
    const crown = union(g.crowns.map(p => box(r, p.position))), tree = union(g.prims.map(p => box(r, p.position)));
    const mat = g.crowns[0].material, tex = mat.pbrMetallicRoughness?.baseColorTexture;
    let rgba = null;
    if (tex && json.textures?.[tex.index]) {
      const t = json.textures[tex.index], src = t.source ?? t.extensions?.EXT_texture_webp?.source;
      if (src !== undefined) rgba = await sharp(r.image(src)).resize(16, 16, { fit: 'fill' }).ensureAlpha().raw().toBuffer();
    }
    const col = leafColour(mat, rgba);
    const ext = json.nodes[g.first].extensions[INST].attributes;
    const T = ext.TRANSLATION !== undefined ? r.accessor(ext.TRANSLATION) : null;
    const R = ext.ROTATION !== undefined ? r.accessor(ext.ROTATION) : null;
    const S = ext.SCALE !== undefined ? r.accessor(ext.SCALE) : null;
    const nw = world.get(g.first);
    for (let i = 0; i < g.count; i++) {
      const m = mul(nw, compose(T ? [...T.subarray(i * 3, i * 3 + 3)] : undefined, R ? [...R.subarray(i * 4, i * 4 + 4)] : undefined, S ? [...S.subarray(i * 3, i * 3 + 3)] : undefined));
      out.push(...record(m, crown, tree, col).map(v => Math.round(v * 1000) / 1000)); // millimetres
    }
  }
  return out;
}

const dir = process.argv[2];
if (!dir) { console.error('usage: node tree_points.mjs DIR'); process.exit(2); }
let files = 0, changed = 0, trees = 0;
for (const f of readdirSync(dir).filter(f => TILE.test(f)).sort()) {
  const lod = join(dir, 'lod', f); if (!existsSync(lod)) continue;
  const recs = await standIns(join(dir, f)); files++; trees += recs.length / 13;
  const { json, bin } = parseGlb(readFileSync(lod)), scene = json.scenes[json.scene ?? 0];
  const before = JSON.stringify(scene.extras?.trees ?? []);
  if (before === JSON.stringify(recs)) continue;
  if (recs.length) scene.extras = { ...scene.extras, trees: recs };
  else if (scene.extras) { delete scene.extras.trees; if (!Object.keys(scene.extras).length) delete scene.extras; }
  writeFileSync(lod + '.tmp', buildGlb(json, bin)); renameSync(lod + '.tmp', lod); changed++;
}
console.log(`tree_points: ${trees} trees in ${files} far versions, ${changed} rewritten`);
