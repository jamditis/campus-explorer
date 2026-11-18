// Join the exported models into one campus: writes models/manifest.json and models/ownership.png.
//
// The viewer shows a single campus. Today it is modelled in two Blender files (main and north) that
// share one origin and overlap in the middle; each holds objects the other lacks, and each has its
// own terrain. Drawing both everywhere doubles the shared buildings and makes the terrains fight.
// The exporter joins meshes by material, so the tiles cannot be merged object by object either.
//
// So the ground is divided instead. This tool reads every tile, marks where each model has
// geometry on a 2 m grid, and gives every cell one owner:
//   main   where the main model has ground or objects (it is the newer, more detailed file)
//   north  where only the north model has them, and inside the PATCHES listed below
//   none   everywhere else (the far-field skirt shows there)
// The viewer discards, per pixel, whatever a cell's owner does not own. Tiles left with nothing
// to show are dropped from the manifest. This is a seam, not a merge: UNVERIFIED until the two
// files are merged in Blender and exported as one scene.
//
//   node tools/web-export/unify.mjs             write the manifest and the ownership map
//   node tools/web-export/unify.mjs --check     fail if the committed files are out of date
//   node tools/web-export/unify.mjs --preview out.png   also write a top-down picture of the result
//   add --dry to leave the committed files alone (for trying a change to PATCHES)
import { readFileSync, writeFileSync } from 'node:fs';
import { deflateSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { MeshoptDecoder } from '../../vendor/addons/libs/meshopt_decoder.module.js';

const MODELS = fileURLToPath(new URL('../../models/', import.meta.url));
const SCENES = ['main', 'north']; // priority order
const CELL = 2;                   // metres per ownership cell
const TILE = 160, MARGIN = 240;   // tile size; the map reaches this far past the outermost tile
const EDGE = 2;                   // cells of overlap kept along a border so no gap opens between surfaces
// Far backdrop and mid-distance filler are not campus ground: they never claim a cell.
const NOT_GROUND = /^(BD_|MID_|Roads_OSM|Footpaths_OSM|Footpath control)/;
// Rectangles (viewer x and z, metres) where the north model wins although the main model has ground
// there, because the main file only has a placeholder. Checked in the top-down preview. UNVERIFIED.
const PATCHES = [
  { name: 'University Hall', owner: 'north', x0: -208, z0: -322, x1: -110, z1: -214 },
  { name: 'Softball stadium west of Dickson Hall', owner: 'north', x0: -322, z0: -166, x1: -222, z1: -28 },
];
export const VALUE = { none: 0, northEdge: 100, north: 128, mainEdge: 228, main: 255 };

const TYPES = { 5120: ['getInt8', 1, 127], 5121: ['getUint8', 1, 255], 5122: ['getInt16', 2, 32767], 5123: ['getUint16', 2, 65535], 5125: ['getUint32', 4, 1], 5126: ['getFloat32', 4, 1] };
const WIDTH = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 };

/** Parse a GLB with meshopt-compressed buffers. Returns its JSON and an accessor reader. */
function readGlb(path) {
  const buf = readFileSync(path), jsonLength = buf.readUInt32LE(12);
  const json = JSON.parse(buf.subarray(20, 20 + jsonLength).toString()), bin = buf.subarray(28 + jsonLength);
  const views = json.bufferViews.map(v => {
    const e = v.extensions?.EXT_meshopt_compression;
    if (!e) return { data: bin.subarray(v.byteOffset ?? 0, (v.byteOffset ?? 0) + v.byteLength), stride: v.byteStride };
    const data = new Uint8Array(e.count * e.byteStride);
    MeshoptDecoder.decodeGltfBuffer(data, e.count, e.byteStride, bin.subarray(e.byteOffset ?? 0, (e.byteOffset ?? 0) + e.byteLength), e.mode, e.filter);
    return { data, stride: e.byteStride };
  });
  const accessor = i => {
    const a = json.accessors[i], v = views[a.bufferView], n = WIDTH[a.type], [get, size, norm] = TYPES[a.componentType];
    const stride = v.stride || n * size, out = new Float32Array(a.count * n), k = a.normalized ? 1 / norm : 1;
    const dv = new DataView(v.data.buffer, v.data.byteOffset, v.data.byteLength);
    for (let j = 0; j < a.count; j++) for (let c = 0; c < n; c++) out[j * n + c] = dv[get]((a.byteOffset ?? 0) + j * stride + c * size, true) * k;
    return out;
  };
  return { json, accessor };
}

/** Call `each(ax, ay, az, bx, by, bz, cx, cy, cz, colour)` for every ground-relevant triangle of a tile, in viewer space. */
function triangles(path, each) {
  const { json, accessor } = readGlb(path);
  for (const node of json.nodes) {
    if (node.mesh === undefined || node.extensions?.EXT_mesh_gpu_instancing || NOT_GROUND.test(node.name ?? '')) continue;
    const t = node.translation ?? [0, 0, 0], s = node.scale ?? [1, 1, 1];
    for (const prim of json.meshes[node.mesh].primitives) {
      const pos = accessor(prim.attributes.POSITION), index = prim.indices === undefined ? null : accessor(prim.indices);
      const colour = json.materials?.[prim.material]?.pbrMetallicRoughness?.baseColorFactor ?? [0.7, 0.7, 0.7];
      const n = index ? index.length : pos.length / 3, p = new Float64Array(9);
      for (let i = 0; i < n; i += 3) {
        for (let c = 0; c < 3; c++) { const k = (index ? index[i + c] : i + c) * 3; p[c * 3] = pos[k] * s[0] + t[0]; p[c * 3 + 1] = pos[k + 1] * s[1] + t[1]; p[c * 3 + 2] = pos[k + 2] * s[2] + t[2]; }
        each(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], colour);
      }
    }
  }
}

/** A grid over the campus. `mark` and `paint` rasterize triangles seen from above. */
function makeGrid(box, cell) {
  const w = Math.ceil((box.x1 - box.x0) / cell), h = Math.ceil((box.z1 - box.z0) / cell);
  const col = x => Math.floor((x - box.x0) / cell), row = z => Math.floor((z - box.z0) / cell);
  function cover(ax, az, bx, bz, cx, cz, hit) {
    const c0 = Math.max(0, col(Math.min(ax, bx, cx))), c1 = Math.min(w - 1, col(Math.max(ax, bx, cx)));
    const r0 = Math.max(0, row(Math.min(az, bz, cz))), r1 = Math.min(h - 1, row(Math.max(az, bz, cz)));
    if (c0 > c1 || r0 > r1) return;
    const den = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz);
    for (let r = r0; r <= r1; r++) for (let c = c0; c <= c1; c++) {
      const x = box.x0 + (c + 0.5) * cell, z = box.z0 + (r + 0.5) * cell;
      // small triangles miss cell centres: a triangle that fits in one cell always counts
      let u = 1 / 3, v = 1 / 3;
      if (c0 !== c1 || r0 !== r1) {
        if (Math.abs(den) < 1e-12) continue;
        u = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / den; v = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / den;
        if (u < -0.02 || v < -0.02 || u + v > 1.02) continue;
      }
      hit(r * w + c, u, v);
    }
  }
  return { w, h, box, cell, cover, col, row };
}

function footprint(grid, files) {
  const mask = new Uint8Array(grid.w * grid.h);
  for (const f of files) triangles(f, (ax, ay, az, bx, by, bz, cx, cy, cz) => grid.cover(ax, az, bx, bz, cx, cz, i => { mask[i] = 1; }));
  return mask;
}
/** Grow (`on` = 1) or shrink (`on` = 0) a mask by `r` cells, with a square brush. */
function morph(mask, w, h, r, on) {
  let src = mask;
  for (let pass = 0; pass < r; pass++) {
    const out = src.slice();
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = y * w + x; if (src[i] === on) continue;
      if ((x > 0 && src[i - 1] === on) || (x < w - 1 && src[i + 1] === on) || (y > 0 && src[i - w] === on) || (y < h - 1 && src[i + w] === on)) out[i] = on;
    }
    src = out;
  }
  return src;
}
const near = (mask, w, h, r) => morph(mask, w, h, r, 1);

function png(width, height, channels, pixels) {
  const table = new Uint32Array(256).map((_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
  const crc = b => { let c = ~0; for (const x of b) c = table[(c ^ x) & 255] ^ (c >>> 8); return ~c >>> 0; };
  const chunk = (type, data) => { const head = Buffer.alloc(4); head.writeUInt32BE(data.length); const body = Buffer.concat([Buffer.from(type), data]); const tail = Buffer.alloc(4); tail.writeUInt32BE(crc(body)); return Buffer.concat([head, body, tail]); };
  const row = width * channels, raw = Buffer.alloc((row + 1) * height);
  for (let y = 0; y < height; y++) Buffer.from(pixels.buffer, pixels.byteOffset + y * row, row).copy(raw, y * (row + 1) + 1);
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(width, 0); ihdr.writeUInt32BE(height, 4); ihdr[8] = 8; ihdr[9] = channels === 1 ? 0 : 2;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw, { level: 9 })), chunk('IEND', Buffer.alloc(0))]);
}

/** Does the viewer draw a model's surface in a cell with this ownership value? Mirrors the shader in look.js. */
export function shows(group, value) {
  if (group === 'main') return !(value === VALUE.north || value === VALUE.northEdge);
  if (group === 'north') return value !== VALUE.main;
  return value !== VALUE.north; // skirt
}

function build() {
  const manifests = Object.fromEntries(SCENES.map(s => [s, JSON.parse(readFileSync(`${MODELS}${s}/manifest.json`, 'utf8'))]));
  const centres = SCENES.flatMap(s => manifests[s].tiles.filter(t => t.center).map(t => t.center));
  const snap = (v, up) => (up ? Math.ceil : Math.floor)(v / TILE) * TILE;
  const box = {
    x0: snap(Math.min(...centres.map(c => c[0])) - TILE / 2 - MARGIN), x1: snap(Math.max(...centres.map(c => c[0])) + TILE / 2 + MARGIN, true),
    z0: snap(Math.min(...centres.map(c => c[1])) - TILE / 2 - MARGIN), z1: snap(Math.max(...centres.map(c => c[1])) + TILE / 2 + MARGIN, true),
  };
  const grid = makeGrid(box, CELL), { w, h } = grid;
  const path = (scene, t) => `${MODELS}${scene}/${t.file}`;
  const ground = scene => manifests[scene].tiles.filter(t => t.file !== 'skirt.glb');
  const tileMask = {}, foot = {};
  for (const scene of SCENES) {
    foot[scene] = new Uint8Array(w * h);
    for (const t of ground(scene)) {
      const m = tileMask[`${scene}/${t.file}`] = footprint(grid, [path(scene, t)]);
      for (let i = 0; i < m.length; i++) if (m[i]) foot[scene][i] = 1;
    }
  }
  // close pinholes in the main footprint so the north terrain cannot show through them
  const main = morph(near(foot.main, w, h, 2), w, h, 2, 0), north = foot.north;
  const owner = new Uint8Array(w * h); // 0 none, 1 north, 2 main
  for (let i = 0; i < owner.length; i++) owner[i] = main[i] ? 2 : north[i] ? 1 : 0;
  for (const p of PATCHES) {
    const want = p.owner === 'main' ? 2 : 1, has = p.owner === 'main' ? main : north;
    for (let r = Math.max(0, grid.row(p.z0)); r <= Math.min(h - 1, grid.row(p.z1)); r++) for (let c = Math.max(0, grid.col(p.x0)); c <= Math.min(w - 1, grid.col(p.x1)); c++) if (has[r * w + c]) owner[r * w + c] = want;
  }
  // borders: keep a strip where both neighbours draw, so a height difference never opens a gap
  const notMain = near(Uint8Array.from(owner, v => +(v !== 2)), w, h, EDGE), isNone = near(Uint8Array.from(owner, v => +(v === 0)), w, h, EDGE);
  const map = new Uint8Array(w * h);
  for (let i = 0; i < map.length; i++) map[i] = owner[i] === 2 ? (notMain[i] ? VALUE.mainEdge : VALUE.main) : owner[i] === 1 ? (isNone[i] ? VALUE.northEdge : VALUE.north) : VALUE.none;

  // one tile list: shared tiles first, then every centred tile that still has something to show
  const tiles = [], dropped = [];
  for (const scene of SCENES) for (const t of manifests[scene].tiles) {
    const entry = { ...t, file: `${scene}/${t.file}`, scene };
    if (t.file === 'skirt.glb') { if (scene === SCENES[0]) tiles.push({ ...entry, scene: 'skirt' }); continue; }
    const m = tileMask[entry.file]; let shown = 0, total = 0;
    for (let i = 0; i < m.length; i++) if (m[i]) { total++; if (shows(scene, map[i])) shown++; }
    // instanced trees and lamps are not in the footprint; a tile with no ground of its own is kept
    if (t.center && total > 0 && shown < Math.min(25, total * 0.5)) { dropped.push({ file: entry.file, bytes: t.bytes, reason: 'every cell it covers belongs to the other model' }); continue; }
    tiles.push(entry);
  }
  const rank = t => (t.center ? 2 : t.file.endsWith('skirt.glb') ? 0 : 1);
  tiles.sort((a, b) => rank(a) - rank(b) || SCENES.indexOf(a.scene) - SCENES.indexOf(b.scene) || (a.file < b.file ? -1 : 1));
  const manifest = {
    tiles,
    paint: SCENES.flatMap(s => manifests[s].paint.map(p => ({ ...p, file: `${s}/${p.file}` }))),
    ownership: { file: 'ownership.png', x0: box.x0, z0: box.z0, x1: box.x0 + w * CELL, z1: box.z0 + h * CELL, cell: CELL, values: VALUE, patches: PATCHES },
    sources: SCENES.map(s => ({ scene: s, source_saved: manifests[s].source_saved ?? '', source_version: manifests[s].source_version ?? '', exported: manifests[s].exported ?? '' })),
    dropped,
    total_bytes: tiles.reduce((sum, t) => sum + t.bytes, 0),
  };
  return { manifest, map, grid, manifests };
}

/** Top-down picture of what the viewer will draw: each model's colours, cut by the ownership map. */
function preview(file, { manifest, map, grid }, scale = 1) {
  const o = manifest.ownership, fine = makeGrid({ x0: o.x0, z0: o.z0, x1: o.x1, z1: o.z1 }, 1 / scale), { w, h } = fine;
  const depth = new Float32Array(w * h).fill(-1e9), rgb = new Uint8Array(w * h * 3).fill(38), tone = c => 255 * Math.pow(Math.min(1, Math.max(0, c)), 1 / 2.2);
  for (const t of manifest.tiles) {
    triangles(`${MODELS}${t.file}`, (ax, ay, az, bx, by, bz, cx, cy, cz, colour) => {
      const nx = (by - ay) * (cz - az) - (bz - az) * (cy - ay), ny = (bz - az) * (cx - ax) - (bx - ax) * (cz - az), nz = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax);
      const shade = 0.6 + 0.4 * Math.abs(ny) / (Math.hypot(nx, ny, nz) || 1);
      fine.cover(ax, az, bx, bz, cx, cz, (i, u, v) => {
        const x = fine.box.x0 + (i % w + 0.5) / scale, z = fine.box.z0 + (Math.floor(i / w) + 0.5) / scale;
        if (!shows(t.scene, map[grid.row(z) * grid.w + grid.col(x)])) return;
        const y = u * ay + v * by + (1 - u - v) * cy;
        if (y <= depth[i]) return;
        depth[i] = y; for (let c = 0; c < 3; c++) rgb[i * 3 + c] = tone(colour[c]) * shade;
      });
    });
  }
  writeFileSync(file, png(w, h, 3, rgb));
}

await MeshoptDecoder.ready;
const args = process.argv.slice(2), result = build();
const json = `${JSON.stringify(result.manifest, null, 1)}\n`, image = png(result.grid.w, result.grid.h, 1, result.map);
if (args.includes('--check')) {
  const same = readFileSync(`${MODELS}manifest.json`, 'utf8') === json && readFileSync(`${MODELS}ownership.png`).equals(image);
  console.log(same ? 'unify: models/manifest.json and models/ownership.png are current' : 'unify: out of date. Run node tools/web-export/unify.mjs and commit the result');
  process.exit(same ? 0 : 1);
}
if (!args.includes('--dry')) { writeFileSync(`${MODELS}manifest.json`, json); writeFileSync(`${MODELS}ownership.png`, image); }
const m = result.manifest, count = v => result.map.reduce((n, x) => n + (x === v), 0) * CELL * CELL / 1e4;
console.log(`unify: ${m.tiles.length} tiles, ${(m.total_bytes / 1e6).toFixed(0)} MB; main owns ${(count(VALUE.main) + count(VALUE.mainEdge)).toFixed(1)} ha, north ${(count(VALUE.north) + count(VALUE.northEdge)).toFixed(1)} ha`);
for (const d of m.dropped) console.log(`  not listed: ${d.file} (${(d.bytes / 1e6).toFixed(1)} MB): ${d.reason}`);
const at = args.indexOf('--preview');
if (at >= 0) { preview(args[at + 1], result, Number(args[at + 2]) || 1); console.log(`preview: ${args[at + 1]}`); }
