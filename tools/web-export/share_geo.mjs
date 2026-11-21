// Store compressed geometry that two or more published files carry byte for byte once, in DIR/geo/<name>.bin, and
// let the files' meshopt views point into it (geoshare.mjs). The tree meshes are the case: each tile carries its
// own copy of every Tree_* mesh it plants, the same bytes in up to 64 files. Views that exactly the same files use
// go in one pack, so a tile never downloads geometry it does not draw. Works on published tiles (DIR/*.glb and
// DIR/lod/*.glb), so it needs no .blend; the data is copied as bytes, never decoded. A pack no file names any more
// is deleted, and a view that is no longer shared goes back into its file.
//   node share_geo.mjs DIR            (build_web.sh runs it after share_tex.mjs, before manifest.py)
//   node share_geo.mjs DIR --embed    (SHARE_GEO=0: every view back inside its file, geo/ removed)
import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync, renameSync, rmSync, statSync, rmdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { parseGlb, buildGlb } from './tex.mjs';
import { compressedViews, planPacks, packBytes, relink, geoUri, geoName } from './geoshare.mjs';

const args = process.argv.slice(2), embedAll = args.includes('--embed'), dir = args.find(a => !a.startsWith('--'));
if (!dir) { console.error('usage: node share_geo.mjs DIR [--embed]'); process.exit(2); }
const geoDir = join(dir, 'geo');
const list = d => (existsSync(join(dir, d)) ? readdirSync(join(dir, d)).filter(f => f.endsWith('.glb')).sort().map(f => (d ? `${d}/${f}` : f)) : []);
const files = [...list(''), ...list('lod')];
const size = f => statSync(f).size;
const geoFiles = () => (existsSync(geoDir) ? readdirSync(geoDir) : []);
const total = () => files.reduce((s, f) => s + size(join(dir, f)), 0) + geoFiles().reduce((s, f) => s + size(join(geoDir, f)), 0);
const before = total();

function read(file) {
  const raw = readFileSync(join(dir, file)), { json, bin } = parseGlb(raw);
  const views = compressedViews(json, bin, uri => {
    const at = resolve(dir, dirname(file), uri);
    if (at !== resolve(geoDir, geoName(uri))) throw new Error(`${file}: ${uri} is not in ${geoDir}`);
    return readFileSync(at);
  });
  return { raw, json, bin, views };
}
// pass 1: which files use each view
const uses = new Map();
for (const f of files) {
  for (const v of read(f).views) {
    if (!uses.has(v.key)) uses.set(v.key, { size: v.bytes.byteLength, files: new Set() });
    uses.get(v.key).files.add(f);
  }
}
const packs = embedAll ? [] : planPacks(uses), packOf = new Map();
for (const p of packs) for (const k of p.keys) packOf.set(k, p);
// pass 2: write the packs before any file names them
const put = (path, bytes) => { writeFileSync(path + '.part', bytes); renameSync(path + '.part', path); };
const want = new Map(), have = new Map();
for (const p of packs) if (!existsSync(join(geoDir, p.name))) for (const k of p.keys) want.set(k, p);
for (const f of files) {
  if (!want.size) break;
  for (const v of read(f).views) if (want.has(v.key) && !have.has(v.key)) have.set(v.key, Buffer.from(v.bytes));
}
if (packs.length) mkdirSync(geoDir, { recursive: true });
let written = 0;
for (const p of new Set(want.values())) { put(join(geoDir, p.name), packBytes(p, k => have.get(k))); written++; }
// pass 3: point every file at the packs
let rewritten = 0;
for (const f of files) {
  const { raw, json, bin, views } = read(f), assign = new Map();
  for (const v of views) {
    const p = packOf.get(v.key);
    if (p) assign.set(v.index, { uri: geoUri(f, p.name), byteOffset: p.offsets.get(v.key), size: p.size });
  }
  // a file with nothing in a pack, before or after, is left byte for byte as it is
  if (!assign.size && !(json.buffers || []).some(b => geoName(b.uri))) continue;
  const r = relink(json, bin, views, assign), out = buildGlb(r.json, r.bin);
  if (Buffer.compare(Buffer.from(out), raw) === 0) continue;
  put(join(dir, f), out); rewritten++;
}
const keep = new Set(packs.map(p => p.name));
let pruned = 0;
for (const f of geoFiles()) if (!keep.has(f)) { rmSync(join(geoDir, f)); pruned++; }
if (existsSync(geoDir) && !geoFiles().length) rmdirSync(geoDir);
const geoBytes = geoFiles().reduce((s, f) => s + size(join(geoDir, f)), 0);
console.log(`share geometry: ${files.length} files, ${packs.length} packs (${(geoBytes / 1e6).toFixed(2)} MB; ${written} new, ${pruned} pruned), ` +
  `${rewritten} files rewritten, ${(before / 1e6).toFixed(2)} -> ${(total() / 1e6).toFixed(2)} MB`);
