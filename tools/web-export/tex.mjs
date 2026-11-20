// Shared tile images: an image that two or more published tiles carry (the leaf textures are in almost
// every tile; a paint sheet is in its tile and in that tile's far version) is stored once, as
// models/main/tex/<content hash>.<ext>, and the tiles refer to it by a relative `uri` instead of a buffer view.
// Pure helpers for share_tex.mjs, compact.mjs and lod.mjs (no gltf-transform); unit-tested from node --test.
// build_web.sh copies this file next to those scripts before it runs them.
import { createHash } from 'node:crypto';
import { posix } from 'node:path';

const JSON_CHUNK = 0x4e4f534a, BIN_CHUNK = 0x004e4942;
const EXT = { 'image/webp': 'webp', 'image/png': 'png', 'image/jpeg': 'jpg' };
const align = (n, a) => Math.ceil(n / a) * a;

/** GLB bytes -> { json, bin } (bin is a view into the input, or null when the file has no binary chunk). */
export function parseGlb(u8) {
  const dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
  if (dv.getUint32(0, true) !== 0x46546c67) throw new Error('not a GLB');
  let at = 12, json = null, bin = null;
  while (at < u8.byteLength) {
    const len = dv.getUint32(at, true), type = dv.getUint32(at + 4, true), body = u8.subarray(at + 8, at + 8 + len);
    if (type === JSON_CHUNK) json = JSON.parse(new TextDecoder().decode(body));
    else if (type === BIN_CHUNK) bin = body;
    at += 8 + len;
  }
  return { json, bin };
}

/** { json, bin } -> GLB bytes (JSON padded with spaces, binary chunk with zeros, as the format asks). */
export function buildGlb(json, bin) {
  const text = new TextEncoder().encode(JSON.stringify(json));
  const jl = align(text.byteLength, 4), bl = bin ? align(bin.byteLength, 4) : 0;
  const out = new Uint8Array(12 + 8 + jl + (bin ? 8 + bl : 0)), dv = new DataView(out.buffer);
  dv.setUint32(0, 0x46546c67, true); dv.setUint32(4, 2, true); dv.setUint32(8, out.byteLength, true);
  dv.setUint32(12, jl, true); dv.setUint32(16, JSON_CHUNK, true);
  out.fill(0x20, 20, 20 + jl); out.set(text, 20);
  if (bin) { dv.setUint32(20 + jl, bl, true); dv.setUint32(24 + jl, BIN_CHUNK, true); out.set(bin, 28 + jl); }
  return out;
}

/** File name of a shared image: the first 20 hex digits of its SHA-256, and its type's extension; null for other types. */
export function contentName(bytes, mimeType) {
  const ext = EXT[mimeType];
  return ext ? `${createHash('sha256').update(bytes).digest('hex').slice(0, 20)}.${ext}` : null;
}

/** The shared image a URI names (`tex/<hash>.<ext>`, or `../tex/...` from a subfolder), else null. */
export function sharedName(uri) {
  const m = typeof uri === 'string' && /^(?:\.\.\/)*tex\/([0-9a-f]{20}\.(?:webp|png|jpg))$/.exec(uri);
  return m ? m[1] : null;
}

/** URI of shared image `name` from tile `file` (a path relative to models/main, e.g. `lod/t_0_0.glb`). */
export function texUri(file, name) {
  return '../'.repeat(file.split('/').length - 1) + 'tex/' + name;
}

/** Names of the images to share: those that `min` or more files carry. `uses`: Map name -> Set of files. */
export function sharedSet(uses, min = 2) {
  return new Set([...uses].filter(([, files]) => files.size >= min).map(([name]) => name));
}

/**
 * What to change in one file. `images`: [{ index, name, uri }] where `name` is the content name (null for a
 * type that is never shared, and for an external image that is not a shared file) and `uri` the image's URI
 * now (null when embedded). Returns Map index ->
 * { uri } (refer to the shared file) or { embed: name } (carry the image inside the tile again).
 */
export function planFile(file, images, shared) {
  const plan = new Map();
  for (const im of images) {
    if (!im.name) continue;
    if (shared.has(im.name)) {
      const uri = texUri(file, im.name);
      if (im.uri !== uri) plan.set(im.index, { uri });
    } else if (im.uri) plan.set(im.index, { embed: im.name });
  }
  return plan;
}

/** Every image of a tile: { index, bytes (embedded) | null, uri | null, mimeType }. */
export function imagesOf(json, bin) {
  return (json.images || []).map((im, index) => {
    if (im.bufferView === undefined) return { index, bytes: null, uri: im.uri ?? null, mimeType: im.mimeType };
    const v = json.bufferViews[im.bufferView], o = v.byteOffset || 0;
    return { index, bytes: bin.subarray(o, o + v.byteLength), uri: null, mimeType: im.mimeType };
  });
}

// every object in the JSON with an integer `bufferView` (accessors, sparse parts, images, extensions)
function eachViewRef(node, fn) {
  if (Array.isArray(node)) { for (const x of node) eachViewRef(x, fn); return; }
  if (!node || typeof node !== 'object') return;
  if (Number.isInteger(node.bufferView)) fn(node);
  for (const k in node) if (node[k] && typeof node[k] === 'object') eachViewRef(node[k], fn);
}

/**
 * Apply a plan to one tile. `actions`: Map image index -> { uri } (drop the image's bytes, refer to `uri`)
 * or { bytes } (store these bytes in the tile). Rebuilds the binary chunk: data that stays keeps its order
 * and its offset within its run; runs start on 16 bytes. Buffer views after a dropped one are renumbered
 * wherever the JSON names them. Geometry is copied as bytes, never decoded. Returns a new { json, bin }.
 */
export function rewriteGlb(json0, bin, actions) {
  const json = structuredClone(json0);
  const drop = new Set();
  for (const [i, a] of actions) if (a.uri && json.images[i].bufferView !== undefined) drop.add(json.images[i].bufferView);
  // ranges of buffer 0 still in use: plain views and the compressed data of meshopt views
  const refs = [];
  json.bufferViews.forEach((v, i) => {
    if (drop.has(i)) return;
    const m = v.extensions?.EXT_meshopt_compression;
    if (v.buffer === 0) refs.push(v);
    if (m && m.buffer === 0) refs.push(m);
  });
  refs.sort((a, b) => (a.byteOffset || 0) - (b.byteOffset || 0));
  const runs = [];
  for (const r of refs) {
    const s = r.byteOffset || 0, e = s + r.byteLength, last = runs.at(-1);
    if (last && s < last.end) { last.end = Math.max(last.end, e); last.refs.push(r); } else runs.push({ start: s, end: e, refs: [r] });
  }
  const embeds = [...actions].filter(([, a]) => a.bytes);
  let size = 0;
  for (const run of runs) { run.to = align(size, 16); size = run.to + run.end - run.start; }
  const placed = embeds.map(([i, a]) => { const to = align(size, 16); size = to + a.bytes.byteLength; return [i, a.bytes, to]; });
  const out = new Uint8Array(align(size, 4));
  for (const run of runs) {
    out.set(bin.subarray(run.start, run.end), run.to);
    for (const r of run.refs) r.byteOffset = run.to + (r.byteOffset || 0) - run.start;
  }
  // renumber views, then drop the moved images' views
  const map = new Map(); let n = 0;
  json.bufferViews.forEach((_, i) => { if (!drop.has(i)) map.set(i, n++); });
  eachViewRef(json, o => { o.bufferView = map.get(o.bufferView); });
  json.bufferViews = json.bufferViews.filter((_, i) => !drop.has(i));
  for (const [i, a] of actions) if (a.uri) { delete json.images[i].bufferView; json.images[i].uri = a.uri; }
  for (const [i, bytes, to] of placed) {
    out.set(bytes, to);
    delete json.images[i].uri; json.images[i].bufferView = json.bufferViews.length;
    json.bufferViews.push({ buffer: 0, byteOffset: to, byteLength: bytes.byteLength });
  }
  json.buffers[0].byteLength = out.byteLength;
  return { json, bin: out };
}

/**
 * The shared files a tile named when a tool read it, as Map name -> URI from the file the tool writes.
 * `uris`: the URIs of the tile's images as read (gltf-transform Texture.getURI()); paths are POSIX.
 */
export function sharedRefs(uris, inFile, outFile) {
  const refs = new Map();
  for (const uri of uris) {
    const name = sharedName(uri); if (!name) continue;
    refs.set(name, posix.relative(posix.dirname(outFile), posix.join(posix.dirname(inFile), uri)));
  }
  return refs;
}

/**
 * gltf-transform writes every image of a GLB into the file. After a tool (compact.mjs, lod.mjs) wrote a tile,
 * refer again to the shared files the tile named (`refs`, from sharedRefs). The name is the content hash, so an
 * image the tool changed (lod.mjs halves them) does not match and stays inside; share_tex.mjs sorts that out.
 */
export function keepShared(glb, refs) {
  if (!refs.size) return glb;
  const { json, bin } = parseGlb(glb), actions = new Map();
  for (const im of imagesOf(json, bin)) {
    const name = im.bytes && contentName(im.bytes, im.mimeType);
    if (name && refs.has(name)) actions.set(im.index, { uri: refs.get(name) });
  }
  if (!actions.size) return glb;
  const r = rewriteGlb(json, bin, actions);
  return buildGlb(r.json, r.bin);
}
