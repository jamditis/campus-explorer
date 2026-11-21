// Store instance transforms (EXT_mesh_gpu_instancing) through the meshopt filters made for them: EXPONENTIAL for
// translations and scales, QUATERNION for rotations. gltf-transform filters only normals and animation, so the
// instance data went in as raw floats and int16 quaternions, which barely compress: 22 MB of models/main when this
// was written, most of it the main model's 900,000 shrub leaf cards. Each batch gets the fewest bits that keep every
// vertex of its mesh within TOL (1 mm by default) of where the stored transform put it, measured on the decoded
// values (pack.mjs instanceShift); a batch with no such encoding, or none smaller, is left as it is.
//   node inst_filter.mjs FILE.glb [FILE.glb ...]   (rewrites a file in place only when it gets smaller)
// Byte-level: the rest of the file is copied, never decoded. Run it after the last step that writes tiles through
// gltf-transform (drop_zero.mjs), which would store the transforms unfiltered again; a filtered batch is skipped.
import { readFileSync, writeFileSync, renameSync } from 'node:fs';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { parseGlb, buildGlb } from './tex.mjs';
import { compactBin } from './geoshare.mjs';
import { instanceShift, unitQuats, decodeUnit, fewestBits } from './pack.mjs';

await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const TOL = +(process.env.TOL || 0.001); // metres, the whole move of a vertex
const MESHOPT = 'EXT_meshopt_compression', FLOAT = 5126, SHORT = 5122;
const TYPED = { 5120: Int8Array, 5121: Uint8Array, 5122: Int16Array, 5123: Uint16Array, 5125: Uint32Array, 5126: Float32Array };
const SIZE = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 };

function decodeView(json, bin, i) {
  const m = json.bufferViews[i].extensions[MESHOPT], out = new Uint8Array(m.count * m.byteStride);
  MeshoptDecoder.decodeGltfBuffer(out, m.count, m.byteStride, bin.subarray(m.byteOffset, m.byteOffset + m.byteLength), m.mode, m.filter);
  return out;
}
// an accessor's elements as floats, decoded from its view (meshopt or plain), normalized integers mapped to -1..1
function readAccessor(json, bin, ai) {
  const a = json.accessors[ai], v = json.bufferViews[a.bufferView], n = SIZE[a.type], T = TYPED[a.componentType];
  const m = v.extensions?.[MESHOPT];
  const raw = m ? decodeView(json, bin, a.bufferView) : bin.slice(v.byteOffset || 0, (v.byteOffset || 0) + v.byteLength);
  const size = T.BYTES_PER_ELEMENT, stride = (m ? m.byteStride : v.byteStride) || n * size;
  const el = new T(a.count * n), from = new Uint8Array(el.buffer);
  for (let i = 0; i < a.count; i++) { // packed copy of the elements, then one typed view over it
    const o = (a.byteOffset || 0) + i * stride;
    from.set(raw.subarray(o, o + n * size), i * n * size);
  }
  return a.normalized ? decodeUnit(el) : Float32Array.from(el);
}
// farthest vertex of a mesh from its origin, in its own coordinates (quantized positions decoded)
function meshRadius(json, bin, mesh) {
  let r = 0;
  for (const p of json.meshes[mesh].primitives) {
    const pos = readAccessor(json, bin, p.attributes.POSITION);
    for (let i = 0; i < pos.length; i += 3) r = Math.max(r, Math.hypot(pos[i], pos[i + 1], pos[i + 2]));
  }
  return r;
}
// a view this script may re-encode: meshopt attributes in the binary chunk, unfiltered, holding exactly this accessor
function own(json, ai, type, componentType, stride) {
  const a = json.accessors[ai]; if (!a || a.type !== type || a.componentType !== componentType || a.sparse) return null;
  const v = json.bufferViews[a.bufferView], m = v?.extensions?.[MESHOPT];
  if (!m || m.buffer !== 0 || m.mode !== 'ATTRIBUTES' || (m.filter ?? 'NONE') !== 'NONE' || m.byteStride !== stride) return null;
  if ((a.byteOffset || 0) !== 0 || m.count !== a.count) return null;
  if (json.accessors.some((b, j) => j !== ai && b.bufferView === a.bufferView)) return null;
  return m;
}
const encode = (data, count, stride) => MeshoptEncoder.encodeGltfBuffer(data, count, stride, 'ATTRIBUTES');
const decode = (enc, count, stride, filter) => { const o = new Uint8Array(count * stride); MeshoptDecoder.decodeGltfBuffer(o, count, stride, enc, 'ATTRIBUTES', filter); return o; };
const f32 = u8 => new Float32Array(u8.buffer, u8.byteOffset, u8.byteLength / 4);

let before = 0, after = 0;
for (const f of process.argv.slice(2)) {
  const raw = readFileSync(f), { json, bin } = parseGlb(raw), put = new Map();
  let batches = 0, instances = 0;
  for (const node of json.nodes || []) {
    const at = node.extensions?.EXT_mesh_gpu_instancing?.attributes; if (!at || node.mesh === undefined) continue;
    const mT = at.TRANSLATION !== undefined ? own(json, at.TRANSLATION, 'VEC3', FLOAT, 12) : null;
    const mS = at.SCALE !== undefined ? own(json, at.SCALE, 'VEC3', FLOAT, 12) : null;
    const mR = at.ROTATION !== undefined ? own(json, at.ROTATION, 'VEC4', SHORT, 8) : null;
    if (!mT && !mS && !mR) continue;
    const n = json.accessors[(at.TRANSLATION ?? at.ROTATION ?? at.SCALE)].count;
    const radius = meshRadius(json, bin, node.mesh);
    const T = at.TRANSLATION !== undefined ? readAccessor(json, bin, at.TRANSLATION) : new Float32Array(n * 3);
    const R = at.ROTATION !== undefined ? readAccessor(json, bin, at.ROTATION) : Float32Array.from({ length: n * 4 }, (_, i) => (i % 4 === 3 ? 1 : 0));
    const S = at.SCALE !== undefined ? readAccessor(json, bin, at.SCALE) : new Float32Array(n * 3).fill(1);
    const inst = (t, q, s, i) => ({ t: t.subarray(i * 3, i * 3 + 3), q: q.subarray(i * 4, i * 4 + 4), s: s.subarray(i * 3, i * 3 + 3) });
    const worst = (t, q, s) => { let w = 0; for (let i = 0; i < n; i++) w = Math.max(w, instanceShift(inst(T, R, S, i), inst(t, q, s, i), radius)); return w; };
    // one third of the tolerance each; the joint check below is what decides
    const tries = {};
    const tryExp = (values, bits) => { const e = encode(MeshoptEncoder.encodeFilterExp(values, n, 12, bits, 'Separate'), n, 12); return { e, d: f32(decode(e, n, 12, 'EXPONENTIAL')) }; };
    const tryQuat = bits => { const e = encode(MeshoptEncoder.encodeFilterQuat(unitQuats(R), n, 8, bits), n, 8); return { e, d: decodeUnit(new Int16Array(decode(e, n, 8, 'QUATERNION').buffer)) }; };
    const B24 = Array.from({ length: 17 }, (_, i) => i + 8), B16 = Array.from({ length: 13 }, (_, i) => i + 4);
    const pick = (key, list, make, err) => {
      const b = fewestBits(list, bits => { const r = make(bits); tries[key + bits] = r; return err(r.d); }, TOL / 3);
      return b === null ? null : { ...tries[key + b], bits: b };
    };
    // a batch filtered before and written unfiltered since (a later gltf-transform step) keeps the bits it had, so
    // the error never adds up over runs: re-encoding decoded values at the same bits gives them back
    const prev = node.extras?.inst_bits ?? {}, only = (b, list) => (b ? [b] : list);
    const t = mT && pick('t', only(prev.TRANSLATION, B24), bits => tryExp(T, bits), d => worst(d, R, S));
    const s = mS && pick('s', only(prev.SCALE, B24), bits => tryExp(S, bits), d => worst(T, R, d));
    const q = mR && pick('q', only(prev.ROTATION, B16), tryQuat, d => worst(T, d, S));
    if (worst(t ? t.d : T, q ? q.d : R, s ? s.d : S) > TOL) continue; // never expected: each part is within a third
    let used = false;
    const bits = {};
    for (const [key, m, r, filter] of [['TRANSLATION', mT, t, 'EXPONENTIAL'], ['SCALE', mS, s, 'EXPONENTIAL'], ['ROTATION', mR, q, 'QUATERNION']]) {
      if (!m || !r || r.e.byteLength >= m.byteLength) continue;
      m.filter = filter; put.set(m, r.e); used = true; bits[key] = r.bits;
    }
    if (used) node.extras = { ...node.extras, inst_bits: { ...prev, ...bits } };
    if (used) { batches++; instances += n; }
  }
  before += raw.byteLength;
  if (!put.size) { after += raw.byteLength; continue; }
  const out = buildGlb(json, compactBin(json, bin, put));
  if (out.byteLength >= raw.byteLength) { after += raw.byteLength; continue; } // a few instances: the JSON grows more
  writeFileSync(f + '.part', out); renameSync(f + '.part', f);
  after += out.byteLength;
  console.log(`inst_filter ${f.split('/').pop()}: ${batches} batches, ${instances} instances, ${(raw.byteLength / 1e6).toFixed(2)} -> ${(out.byteLength / 1e6).toFixed(2)} MB`);
}
console.log(`inst_filter: ${(before / 1e6).toFixed(1)} -> ${(after / 1e6).toFixed(1)} MB`);
