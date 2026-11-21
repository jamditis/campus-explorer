import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  geoName, geoUri, viewKey, packName, compressedViews, planPacks, packBytes, compactBin, relink, splitIndexViews,
} from '../tools/web-export/geoshare.mjs';

const bytes = (n, v) => new Uint8Array(n).fill(v);
const ext = (o, n, extra = {}) => ({ buffer: 0, byteOffset: o, byteLength: n, byteStride: 4, count: 10, mode: 'ATTRIBUTES', ...extra });

// A tile: an image (plain view), two compressed views (a tree's positions, 24 bytes of 7; the ground, 8 bytes of 9),
// and a compressed index view; the meshopt fallback buffer is buffer 1.
function tile(tree = 7) {
  const bin = new Uint8Array(96);
  bin.set(bytes(12, 1), 0); bin.set(bytes(24, tree), 16); bin.set(bytes(8, 9), 48); bin.set(bytes(6, 5), 64);
  const json = {
    asset: { version: '2.0' },
    buffers: [{ byteLength: 96 }, { byteLength: 999, extensions: { EXT_meshopt_compression: { fallback: true } } }],
    bufferViews: [
      { buffer: 0, byteOffset: 0, byteLength: 12 },
      { buffer: 1, byteOffset: 0, byteLength: 40, extensions: { EXT_meshopt_compression: ext(16, 24) } },
      { buffer: 1, byteOffset: 40, byteLength: 40, extensions: { EXT_meshopt_compression: ext(48, 8) } },
      { buffer: 1, byteOffset: 80, byteLength: 12, extensions: { EXT_meshopt_compression: ext(64, 6, { byteStride: 2, count: 6, mode: 'TRIANGLES' }) } },
    ],
    images: [{ mimeType: 'image/webp', bufferView: 0 }],
  };
  return { json, bin };
}
const at = (t, i, packs = {}) => {
  const m = t.json.bufferViews[i].extensions?.EXT_meshopt_compression ?? t.json.bufferViews[i];
  const src = m.buffer === 0 || m.buffer === undefined ? t.bin : packs[t.json.buffers[m.buffer].uri];
  return [...src.subarray(m.byteOffset, m.byteOffset + m.byteLength)];
};

test('packs are named geo/<20 hex>.bin, relative to the tile folder', () => {
  const n = '0123456789abcdef0123.bin';
  assert.equal(geoUri('t_0_0.glb', n), `geo/${n}`);
  assert.equal(geoUri('lod/t_0_0.glb', n), `../geo/${n}`);
  assert.equal(geoName(`geo/${n}`), n);
  assert.equal(geoName(`../geo/${n}`), n);
  for (const u of [undefined, 'tex/x.webp', `x/geo/${n}`, 'geo/zz.bin', `geo/${n}.gz`]) assert.equal(geoName(u), null, u);
  assert.match(packName(['a', 'b']), /^[0-9a-f]{20}\.bin$/);
  assert.notEqual(packName(['a', 'b']), packName(['b', 'a']));
});

test('a view is keyed by its bytes and how it decodes', () => {
  const b = bytes(8, 3);
  assert.equal(viewKey(ext(0, 8), b), viewKey(ext(40, 8), b)); // where it lies does not matter
  assert.notEqual(viewKey(ext(0, 8), b), viewKey(ext(0, 8), bytes(8, 4)));
  assert.notEqual(viewKey(ext(0, 8), b), viewKey(ext(0, 8, { filter: 'OCTAHEDRAL' }), b));
  assert.notEqual(viewKey(ext(0, 8), b), viewKey(ext(0, 8, { count: 11 }), b));
});

test('views used by exactly the same files share a pack; small or one-file views stay in their tiles', () => {
  const f = (...x) => new Set(x);
  const uses = new Map([
    ['k1', { size: 20001, files: f('a', 'b', 'c') }],
    ['k2', { size: 3000, files: f('c', 'b', 'a') }], // same files: same pack as k1
    ['k3', { size: 90000, files: f('a') }], // one file: nothing to share
    ['k4', { size: 100, files: f('a', 'c') }], // under the size floor
    ['k5', { size: 20000, files: f('b', 'c') }], // saves 20 kB: under the saving floor
    ['k6', { size: 40000, files: f('a', 'b') }],
  ]);
  const packs = planPacks(uses);
  assert.equal(packs.length, 2);
  const p = packs.find(x => x.keys.includes('k1'));
  assert.deepEqual(p.keys, ['k1', 'k2']);
  assert.equal(p.offsets.get('k1'), 0);
  assert.equal(p.offsets.get('k2'), 20016); // 16-byte aligned
  assert.equal(p.size, 23016);
  assert.deepEqual(packs.find(x => x !== p).keys, ['k6']);
  assert.deepEqual(planPacks(uses).map(x => x.name), packs.map(x => x.name)); // the same plan every run
  const all = packBytes(p, k => bytes(uses.get(k).size, k === 'k1' ? 1 : 2));
  assert.equal(all[0], 1); assert.equal(all[20000], 1); assert.equal(all[20001], 0); assert.equal(all[20016], 2);
});

test('compactBin keeps the ranges in use and places replaced data after them', () => {
  const t = tile(), json = structuredClone(t.json);
  const ground = json.bufferViews[2].extensions.EXT_meshopt_compression;
  json.bufferViews[1].extensions.EXT_meshopt_compression.buffer = 2; // moved out of the chunk
  const bin = compactBin(json, t.bin, new Map([[ground, bytes(3, 8)]]));
  const after = { json, bin };
  assert.deepEqual(at(after, 0), [...bytes(12, 1)]);
  assert.deepEqual(at(after, 3), [...bytes(6, 5)]);
  assert.deepEqual(at(after, 2), [8, 8, 8]);
  assert.equal(ground.byteLength, 3);
  assert.equal(json.buffers[0].byteLength, bin.byteLength);
  assert.ok(bin.byteLength < t.bin.byteLength);
  for (const r of [json.bufferViews[0], json.bufferViews[3].extensions.EXT_meshopt_compression, ground]) assert.equal(r.byteOffset % 16, 0);
});

test('relink moves shared views into packs and back, and the bytes each view decodes stay the same', () => {
  const t = tile(), views = compressedViews(t.json, t.bin, () => { throw new Error('no packs yet'); });
  assert.equal(views.length, 3);
  const name = packName([views[0].key]), uri = geoUri('t_0_0.glb', name);
  const pack = new Uint8Array(40); pack.set(views[0].bytes, 16);
  const out = relink(t.json, t.bin, views, new Map([[1, { uri, byteOffset: 16, size: 40 }]]));
  assert.equal(out.json.buffers.length, 3);
  assert.deepEqual(out.json.buffers[2], { uri, byteLength: 40 });
  assert.deepEqual(out.json.buffers[1], t.json.buffers[1]); // the fallback buffer keeps its place
  for (let i = 0; i < 4; i++) assert.deepEqual(at(out, i, { [uri]: pack }), at(t, i), `view ${i}`);
  assert.ok(out.bin.byteLength < t.bin.byteLength);
  assert.equal(t.json.buffers.length, 2); // the input is not changed
  // read back through the pack, then nothing assigned: every view returns to the tile
  const again = compressedViews(out.json, out.bin, u => { assert.equal(u, uri); return pack; });
  assert.deepEqual(again.map(v => v.key), views.map(v => v.key));
  const back = relink(out.json, out.bin, again, new Map());
  assert.equal(back.json.buffers.length, 2);
  for (let i = 0; i < 4; i++) assert.deepEqual(at(back, i), at(t, i), `view ${i} back`);
  // the same plan twice gives the same file
  const twice = relink(out.json, out.bin, again, new Map([[1, { uri, byteOffset: 16, size: 40 }]]));
  assert.deepEqual(twice.json, out.json);
  assert.deepEqual([...twice.bin], [...out.bin]);
});

test('a buffer that is not a pack is never followed or dropped', () => {
  const t = tile();
  t.json.buffers.push({ uri: 'other.bin', byteLength: 24 });
  t.json.bufferViews[1].extensions.EXT_meshopt_compression.buffer = 2;
  const views = compressedViews(t.json, t.bin, () => { throw new Error('followed'); });
  assert.deepEqual(views.map(v => v.index), [2, 3]);
  const out = relink(t.json, t.bin, views, new Map());
  assert.deepEqual(out.json.buffers[2], { uri: 'other.bin', byteLength: 24 });
  assert.equal(out.json.bufferViews[1].extensions.EXT_meshopt_compression.buffer, 2);
});

test('an index view shared by several primitives is split into one view per accessor', () => {
  // "compressed" here is the raw bytes with a 1-byte header, so the test can see what went where
  const decode = (m, b) => b.slice(1), encode = (raw, count) => { const o = new Uint8Array(raw.length + 1); o[0] = count; o.set(raw, 1); return o; };
  const raw = Uint8Array.from({ length: 24 }, (_, i) => i); // 12 uint16 indices: a 6-index and a 6-index accessor
  const bin = new Uint8Array(64); bin.set(bytes(8, 4), 0); bin[16] = 12; bin.set(raw, 17);
  const json = {
    buffers: [{ byteLength: 64 }, { byteLength: 200 }],
    bufferViews: [
      { buffer: 0, byteOffset: 0, byteLength: 8 },
      { buffer: 1, byteOffset: 100, byteLength: 24, target: 34963, extensions: { EXT_meshopt_compression: { buffer: 0, byteOffset: 16, byteLength: 25, byteStride: 2, count: 12, mode: 'TRIANGLES' } } },
    ],
    accessors: [
      { bufferView: 1, byteOffset: 0, componentType: 5123, count: 6, type: 'SCALAR' },
      { bufferView: 1, byteOffset: 12, componentType: 5123, count: 6, type: 'SCALAR' },
    ],
    meshes: [{ primitives: [{ attributes: {}, indices: 0 }, { attributes: {}, indices: 1 }] }],
  };
  const out = splitIndexViews(json, bin, decode, encode);
  assert.equal(out.json.bufferViews.length, 3);
  const [a, b] = out.json.accessors;
  assert.equal(a.bufferView, 1); assert.equal(b.bufferView, 2);
  assert.equal(a.byteOffset, 0); assert.equal(b.byteOffset, 0);
  const va = out.json.bufferViews[1], vb = out.json.bufferViews[2];
  assert.deepEqual([va.buffer, va.byteOffset, va.byteLength, va.target], [1, 100, 12, 34963]);
  assert.deepEqual([vb.buffer, vb.byteOffset, vb.byteLength, vb.target], [1, 112, 12, 34963]);
  const got = v => { const m = v.extensions.EXT_meshopt_compression; return [...out.bin.subarray(m.byteOffset, m.byteOffset + m.byteLength)]; };
  assert.deepEqual(got(va), [6, ...raw.slice(0, 12)]);
  assert.deepEqual(got(vb), [6, ...raw.slice(12)]);
  assert.equal(vb.extensions.EXT_meshopt_compression.count, 6);
  assert.deepEqual([...out.bin.subarray(0, 8)], [...bytes(8, 4)]); // other data stays
  assert.equal(json.bufferViews.length, 2); // the input is not changed
  assert.equal(splitIndexViews(out.json, out.bin, decode, encode), null); // nothing left to split
});
