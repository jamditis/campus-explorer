// Shared tile geometry: compressed vertex data that two or more published files carry byte for byte (the tree
// meshes: one Tree_* mesh is in up to 64 tiles, 38 MB of copies across models/main when this was written) is
// stored once, in models/main/geo/<name>.bin, and the tiles' meshopt buffer views point into it through a buffer
// with a `uri`, as the glTF spec allows. Pure helpers for share_geo.mjs and inst_filter.mjs (no gltf-transform);
// unit-tested from node --test. build_web.sh copies this file next to those scripts before it runs them.
import { createHash } from 'node:crypto';

const MESHOPT = 'EXT_meshopt_compression';
const align = (n, a) => Math.ceil(n / a) * a;

/** A pack is shared only when it is at least this big and saves at least this much: every pack is one more request. */
export const PACK_MIN_BYTES = 4096, PACK_MIN_SAVING = 32768;

/** The geometry pack a URI names (`geo/<20 hex>.bin`, or `../geo/...` from a subfolder), else null. */
export function geoName(uri) {
  const m = typeof uri === 'string' && /^(?:\.\.\/)*geo\/([0-9a-f]{20}\.bin)$/.exec(uri);
  return m ? m[1] : null;
}

/** URI of pack `name` from file `file` (a path relative to models/main, e.g. `lod/t_0_0.glb`). */
export function geoUri(file, name) {
  return '../'.repeat(file.split('/').length - 1) + 'geo/' + name;
}

/** Content key of one compressed view: its decoding parameters and its bytes. */
export function viewKey(ext, bytes) {
  const { count, byteStride, mode, filter = 'NONE' } = ext;
  return createHash('sha256').update(JSON.stringify([count, byteStride, mode, filter])).update(bytes).digest('hex');
}

/** File name of a pack: the first 20 hex digits of the SHA-256 of its view keys, in order (so of its content). */
export function packName(keys) {
  return createHash('sha256').update(keys.join('\n')).digest('hex').slice(0, 20) + '.bin';
}

/**
 * Every meshopt-compressed view of a tile: [{ index, key, bytes }], with its bytes wherever they are now: in the
 * binary chunk, or in a shared pack (`load(uri)` returns that file's bytes; only geo/ URIs are followed).
 */
export function compressedViews(json, bin, load) {
  const out = [], files = new Map();
  (json.bufferViews || []).forEach((v, index) => {
    const m = v.extensions?.[MESHOPT]; if (!m) return;
    let src = bin;
    if (m.buffer !== 0) {
      const uri = json.buffers[m.buffer]?.uri;
      if (!geoName(uri)) return; // someone else's buffer: left alone
      if (!files.has(uri)) files.set(uri, load(uri));
      src = files.get(uri);
    }
    const o = m.byteOffset || 0, bytes = src.subarray(o, o + m.byteLength);
    if (bytes.byteLength !== m.byteLength) throw new Error(`view ${index}: ${m.byteLength} bytes asked, ${bytes.byteLength} there`);
    out.push({ index, key: viewKey(m, bytes), bytes });
  });
  return out;
}

/**
 * Which views to store once. `uses`: Map key -> { size, files: Set }. Views that exactly the same files use go
 * in one pack, so no file downloads a byte it does not draw; a pack under `minBytes`, or saving under `minSaving`,
 * stays inside its files. Returns [{ name, keys, offsets: Map key -> byte offset, size }], keys in a fixed order.
 */
export function planPacks(uses, { minBytes = PACK_MIN_BYTES, minSaving = PACK_MIN_SAVING } = {}) {
  const groups = new Map();
  for (const [key, u] of uses) {
    if (u.files.size < 2) continue;
    const sig = [...u.files].sort().join('\n');
    if (!groups.has(sig)) groups.set(sig, { keys: [], bytes: 0, files: u.files.size });
    const g = groups.get(sig); g.keys.push(key); g.bytes += u.size;
  }
  const packs = [];
  for (const g of groups.values()) {
    if (g.bytes < minBytes || g.bytes * (g.files - 1) < minSaving) continue;
    const keys = g.keys.sort(), offsets = new Map();
    let at = 0;
    for (const k of keys) { at = align(at, 16); offsets.set(k, at); at += uses.get(k).size; }
    packs.push({ name: packName(keys), keys, offsets, size: at });
  }
  return packs.sort((a, b) => (a.name < b.name ? -1 : 1));
}

/** The bytes of a pack, from `bytesOf(key)`. */
export function packBytes(pack, bytesOf) {
  const out = new Uint8Array(pack.size);
  for (const k of pack.keys) out.set(bytesOf(k), pack.offsets.get(k));
  return out;
}

/**
 * Rebuild buffer 0 (the binary chunk) from the ranges still in it: plain views and the compressed data of meshopt
 * views. `put`: Map ref (a view, or its meshopt extension object, already pointing at buffer 0) -> the bytes it
 * should hold now; those are placed on their own after the rest. Data that stays keeps its order and its offset
 * within its run; runs start on 16 bytes. Changes the offsets in `json` in place; returns the new chunk.
 */
export function compactBin(json, bin, put = new Map()) {
  const refs = [];
  for (const v of json.bufferViews || []) {
    const m = v.extensions?.[MESHOPT];
    if (v.buffer === 0 && !put.has(v)) refs.push(v);
    if (m && m.buffer === 0 && !put.has(m)) refs.push(m);
  }
  refs.sort((a, b) => (a.byteOffset || 0) - (b.byteOffset || 0));
  const runs = [];
  for (const r of refs) {
    const s = r.byteOffset || 0, e = s + r.byteLength, last = runs.at(-1);
    if (last && s < last.end) { last.end = Math.max(last.end, e); last.refs.push(r); } else runs.push({ start: s, end: e, refs: [r] });
  }
  let size = 0;
  for (const run of runs) { run.to = align(size, 16); size = run.to + run.end - run.start; }
  const placed = [...put].map(([ref, bytes]) => { const to = align(size, 16); size = to + bytes.byteLength; return [ref, bytes, to]; });
  const out = new Uint8Array(align(size, 4));
  for (const run of runs) {
    out.set(bin.subarray(run.start, run.end), run.to);
    for (const r of run.refs) r.byteOffset = run.to + (r.byteOffset || 0) - run.start;
  }
  for (const [ref, bytes, to] of placed) { out.set(bytes, to); ref.byteOffset = to; ref.byteLength = bytes.byteLength; }
  if (json.buffers?.[0]) json.buffers[0].byteLength = out.byteLength;
  return out;
}

/**
 * gltf-transform writes the indices of many primitives into one compressed view, so a tree's indices are mixed with
 * the rest of its tile and never match another tile's. Give every index accessor of such a view its own view, so
 * identical index data compresses to identical bytes (+0.7 % index bytes, and 4.3 MB more shared, in models/main
 * when this was written). `decode(ext, bytes)` returns the view's raw bytes; `encode(raw, count, byteStride)` the
 * compressed bytes of an index list (the meshopt codec, injected so this stays pure). The index codec keeps
 * triangle order and winding (it may start a triangle at another corner). Returns a new { json, bin }, or null
 * when no view holds more than one accessor.
 */
export function splitIndexViews(json0, bin, decode, encode) {
  const users = new Map();
  (json0.accessors || []).forEach((a, i) => { if (a.bufferView !== undefined) { if (!users.has(a.bufferView)) users.set(a.bufferView, []); users.get(a.bufferView).push(i); } });
  const indexOf = new Set();
  for (const m of json0.meshes || []) for (const p of m.primitives) if (p.indices !== undefined) indexOf.add(p.indices);
  const split = [...users].filter(([v, list]) => {
    const m = json0.bufferViews[v].extensions?.[MESHOPT];
    return m && m.mode === 'TRIANGLES' && m.buffer === 0 && list.length > 1 && list.every(i => indexOf.has(i) && !json0.accessors[i].sparse);
  });
  if (!split.length) return null;
  const json = structuredClone(json0), put = new Map();
  for (const [vi, list] of split) {
    const v = json.bufferViews[vi], m = v.extensions[MESHOPT];
    const raw = decode(m, bin.subarray(m.byteOffset, m.byteOffset + m.byteLength));
    list.forEach((ai, k) => {
      const a = json.accessors[ai], o = a.byteOffset || 0, len = a.count * m.byteStride;
      const ext = { buffer: 0, byteOffset: 0, byteLength: 0, byteStride: m.byteStride, count: a.count, mode: 'TRIANGLES' };
      const view = { ...v, byteOffset: (v.byteOffset || 0) + o, byteLength: len, extensions: { ...v.extensions, [MESHOPT]: ext } };
      put.set(ext, encode(raw.slice(o, o + len), a.count, m.byteStride));
      if (k === 0) json.bufferViews[vi] = view;
      else { a.bufferView = json.bufferViews.length; json.bufferViews.push(view); }
      a.byteOffset = 0;
    });
  }
  return { json, bin: compactBin(json, bin, put) };
}

/**
 * Point a tile's views at the packs. `views`: compressedViews() of the tile; `assign`: Map view index ->
 * { uri, byteOffset, size } (the pack's URI from this file, the view's offset in it, the pack's size). Every other
 * view that is in a pack now comes back into the binary chunk. Buffers that are not packs keep their order (the
 * binary chunk first, then the meshopt fallback buffer); the packs follow, in URI order. Returns a new { json, bin }.
 */
export function relink(json0, bin, views, assign) {
  const json = structuredClone(json0);
  const keep = [], index = new Map();
  (json.buffers || []).forEach((b, i) => { if (!geoName(b.uri)) { index.set(i, keep.length); keep.push(b); } });
  const uris = [...new Set([...assign.values()].map(a => a.uri))].sort();
  const geo = new Map(uris.map((u, i) => [u, keep.length + i]));
  const sizes = new Map([...assign.values()].map(a => [a.uri, a.size]));
  json.buffers = [...keep, ...uris.map(uri => ({ uri, byteLength: sizes.get(uri) }))];
  const bytesOf = new Map(views.map(v => [v.index, v.bytes]));
  const put = new Map();
  json.bufferViews.forEach((v, i) => {
    if (index.has(v.buffer)) v.buffer = index.get(v.buffer);
    const m = v.extensions?.[MESHOPT]; if (!m) return;
    const a = assign.get(i);
    if (a) { m.buffer = geo.get(a.uri); m.byteOffset = a.byteOffset; return; }
    if (index.has(m.buffer)) { m.buffer = index.get(m.buffer); return; }
    m.buffer = 0; put.set(m, bytesOf.get(i)); // was in a pack: back into the tile
  });
  // views moved out of buffer 0 no longer count as in it; compactBin keeps only refs that still point there
  const out = compactBin(json, bin ?? new Uint8Array(0), put);
  if (!json.buffers.length) delete json.buffers;
  return { json, bin: out };
}
