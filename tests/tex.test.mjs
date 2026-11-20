import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  parseGlb, buildGlb, contentName, sharedName, texUri, sharedSet, planFile, rewriteGlb, imagesOf, sharedRefs, keepShared,
} from '../tools/web-export/tex.mjs';

const bytes = (n, v) => new Uint8Array(n).fill(v);

// A small tile: image 0 (12 bytes), a meshopt-compressed view, image 1 (5 bytes), a plain accessor view.
function tile() {
  const bin = new Uint8Array(64);
  bin.set(bytes(12, 1), 0); bin.set(bytes(8, 2), 16); bin.set(bytes(5, 3), 24); bin.set(bytes(16, 4), 32);
  const json = {
    asset: { version: '2.0' },
    buffers: [{ byteLength: 64 }, { byteLength: 400, extensions: { EXT_meshopt_compression: { fallback: true } } }],
    bufferViews: [
      { buffer: 0, byteOffset: 0, byteLength: 12 },
      { buffer: 1, byteOffset: 0, byteLength: 400, extensions: { EXT_meshopt_compression: { buffer: 0, byteOffset: 16, byteLength: 8, byteStride: 4, count: 100, mode: 'ATTRIBUTES' } } },
      { buffer: 0, byteOffset: 24, byteLength: 5 },
      { buffer: 0, byteOffset: 32, byteLength: 16 },
    ],
    accessors: [{ bufferView: 1, componentType: 5126, count: 100, type: 'SCALAR' }, { bufferView: 3, componentType: 5126, count: 4, type: 'SCALAR' }],
    images: [{ name: 'leaf', mimeType: 'image/webp', bufferView: 0 }, { name: 'paint', mimeType: 'image/png', bufferView: 2 }],
    textures: [{ extensions: { EXT_texture_webp: { source: 0 } } }, { source: 1 }],
  };
  return { json, bin };
}
// the bytes a buffer view (or its meshopt data) points at
const viewBytes = ({ json, bin }, i) => {
  const v = json.bufferViews[i], m = v.extensions?.EXT_meshopt_compression, r = m ?? v;
  return [...bin.subarray(r.byteOffset, r.byteOffset + r.byteLength)];
};

test('a GLB survives a parse and build with its JSON and binary chunk', () => {
  const t = tile(), back = parseGlb(buildGlb(t.json, t.bin));
  assert.deepEqual(back.json, t.json);
  assert.deepEqual([...back.bin], [...t.bin]);
  const glb = buildGlb(t.json, t.bin);
  assert.equal(glb.byteLength % 4, 0);
  assert.equal(new DataView(glb.buffer).getUint32(8, true), glb.byteLength);
});

test('shared images are named by content hash, with the extension of their type', () => {
  const a = contentName(bytes(12, 1), 'image/webp');
  assert.match(a, /^[0-9a-f]{20}\.webp$/);
  assert.equal(contentName(bytes(12, 1), 'image/webp'), a);
  assert.notEqual(contentName(bytes(12, 2), 'image/webp'), a);
  assert.match(contentName(bytes(3, 9), 'image/jpeg'), /\.jpg$/);
  assert.equal(contentName(bytes(3, 9), 'image/ktx2'), null); // not a type the viewer loads by URI
});

test('a tile refers to a shared image relative to its own folder', () => {
  assert.equal(texUri('t_0_0.glb', 'ab.webp'), 'tex/ab.webp');
  assert.equal(texUri('lod/t_0_0.glb', 'ab.webp'), '../tex/ab.webp');
  const n = '0123456789abcdef0123.webp';
  assert.equal(sharedName(`tex/${n}`), n);
  assert.equal(sharedName(`../tex/${n}`), n);
  for (const u of [undefined, 'leaf.webp', 'data:image/webp;base64,AA', `x/tex/${n}`, 'tex/zz.webp']) assert.equal(sharedName(u), null, u);
});

test('an image is shared when two or more tiles carry it; one tile keeps its own', () => {
  const uses = new Map([['a.webp', new Set(['t_0_0.glb', 'lod/t_0_0.glb'])], ['b.webp', new Set(['t_0_0.glb'])]]);
  assert.deepEqual([...sharedSet(uses)], ['a.webp']);
  assert.deepEqual([...sharedSet(uses, Infinity)], []); // SHARE_TEX=0: nothing shared, everything embedded again
});

test('the plan moves shared images out, takes single ones back in, and leaves the rest', () => {
  const shared = new Set(['a.webp', 'c.webp']);
  const images = [
    { index: 0, name: 'a.webp', uri: null },            // embedded, shared -> out
    { index: 1, name: 'b.webp', uri: 'tex/b.webp' },    // external, no longer shared -> back in
    { index: 2, name: 'c.webp', uri: '../tex/c.webp' }, // already right
    { index: 3, name: 'd.webp', uri: null },            // embedded, single
    { index: 4, name: null, uri: null },                // a type that is never shared
  ];
  const plan = planFile('lod/t_0_0.glb', images, shared);
  assert.deepEqual([...plan], [[0, { uri: '../tex/a.webp' }], [1, { embed: 'b.webp' }]]);
  // a full tile names the same image from its own folder
  assert.deepEqual([...planFile('t_0_0.glb', [{ index: 2, name: 'c.webp', uri: '../tex/c.webp' }], shared)], [[2, { uri: 'tex/c.webp' }]]);
});

test('moving an image out drops its bytes and renumbers the buffer views after it', () => {
  const t = tile(), want1 = viewBytes(t, 1), want3 = viewBytes(t, 3);
  const r = rewriteGlb(t.json, t.bin, new Map([[0, { uri: 'tex/a.webp' }]]));
  assert.equal(r.json.images[0].uri, 'tex/a.webp');
  assert.equal(r.json.images[0].bufferView, undefined);
  assert.equal(r.json.images[0].mimeType, 'image/webp');
  assert.equal(r.json.bufferViews.length, 3);
  assert.equal(r.json.accessors[0].bufferView, 0);
  assert.equal(r.json.accessors[1].bufferView, 2);
  assert.equal(r.json.images[1].bufferView, 1);
  assert.deepEqual(viewBytes(r, 0), want1); // meshopt data follows its view
  assert.deepEqual(viewBytes(r, 2), want3);
  assert.equal(r.json.buffers[0].byteLength, r.bin.byteLength);
  assert.ok(r.bin.byteLength < t.bin.byteLength);
  assert.equal(r.json.buffers[1].byteLength, 400); // the meshopt fallback buffer is untouched
  for (const v of r.json.bufferViews) {
    const o = (v.extensions?.EXT_meshopt_compression ?? v).byteOffset;
    assert.equal(o % 4, 0);
  }
  assert.equal(t.json.images[0].bufferView, 0); // the input is not changed
});

test('taking an image back in appends its bytes as a new buffer view', () => {
  const t = tile(), out = rewriteGlb(t.json, t.bin, new Map([[0, { uri: 'tex/a.webp' }]]));
  const back = rewriteGlb(out.json, out.bin, new Map([[0, { bytes: bytes(12, 1) }]]));
  const v = back.json.images[0].bufferView;
  assert.equal(back.json.images[0].uri, undefined);
  assert.deepEqual(viewBytes(back, v), [...bytes(12, 1)]);
  assert.deepEqual(viewBytes(back, back.json.accessors[0].bufferView), viewBytes(t, 1));
});

test('imagesOf lists each image with its bytes (embedded) or its URI (external)', () => {
  const t = tile(), r = rewriteGlb(t.json, t.bin, new Map([[0, { uri: 'tex/a.webp' }]]));
  const list = imagesOf(r.json, r.bin);
  assert.equal(list[0].uri, 'tex/a.webp'); assert.equal(list[0].bytes, null);
  assert.deepEqual([...list[1].bytes], [...bytes(5, 3)]); assert.equal(list[1].mimeType, 'image/png');
});

test('a tool that writes a tile elsewhere names the shared files from its output folder', () => {
  const n = '0123456789abcdef0123.webp';
  const refs = sharedRefs([`tex/${n}`, 'other.webp', null], 'models/main/t_0_0.glb', 'models/main/lod/t_0_0.glb');
  assert.deepEqual([...refs], [[n, `../tex/${n}`]]);
  assert.deepEqual([...sharedRefs([`tex/${n}`], '/a/m/t.glb', '/a/m/t.glb')], [[n, `tex/${n}`]]);
});

test('keepShared moves an image back out after a tool embedded it, unless the tool changed it', () => {
  const t = tile(), name = contentName(bytes(12, 1), 'image/webp');
  const glb = buildGlb(t.json, t.bin);
  const kept = parseGlb(keepShared(glb, new Map([[name, `tex/${name}`]])));
  assert.equal(kept.json.images[0].uri, `tex/${name}`);
  assert.ok(kept.bin.byteLength < t.bin.byteLength);
  assert.equal(kept.json.images[1].bufferView, 1);
  // changed bytes have another name: the image stays in the tile
  const other = parseGlb(keepShared(glb, new Map([[contentName(bytes(12, 7), 'image/webp'), 'tex/x.webp']])));
  assert.equal(other.json.images[0].bufferView, 0);
  assert.equal(keepShared(glb, new Map()), glb);
});
