// Store each image that two or more published tiles carry once, as DIR/tex/<content hash>.<ext>, and let the
// tiles refer to it by URI (tex.mjs). Works on published tiles (DIR/*.glb and DIR/lod/*.glb), so it needs no
// .blend. An image only one tile carries stays inside that tile; a shared file no tile names any more is
// deleted; an image that is no longer shared goes back into its tile. Geometry bytes are copied, not decoded.
//   node share_tex.mjs DIR            (build_web.sh runs it last, before manifest.py)
//   node share_tex.mjs DIR --embed    (SHARE_TEX=0: every image back inside its tile, tex/ removed)
import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync, renameSync, rmSync, statSync, rmdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { parseGlb, buildGlb, contentName, sharedName, sharedSet, planFile, rewriteGlb, imagesOf } from './tex.mjs';

const args = process.argv.slice(2), embedAll = args.includes('--embed'), dir = args.find(a => !a.startsWith('--'));
if (!dir) { console.error('usage: node share_tex.mjs DIR [--embed]'); process.exit(2); }
const texDir = join(dir, 'tex');
const list = d => (existsSync(join(dir, d)) ? readdirSync(join(dir, d)).filter(f => f.endsWith('.glb')).sort().map(f => (d ? `${d}/${f}` : f)) : []);
const files = [...list(''), ...list('lod')];
const size = f => statSync(f).size;
const texFiles = () => (existsSync(texDir) ? readdirSync(texDir) : []);
const before = files.reduce((s, f) => s + size(join(dir, f)), 0) + texFiles().reduce((s, f) => s + size(join(texDir, f)), 0);

// what each file carries, by content name; an external image must be a shared file whose bytes match its name
function read(file) {
  const { json, bin } = parseGlb(readFileSync(join(dir, file)));
  const images = imagesOf(json, bin).map(im => {
    if (im.bytes) return { ...im, name: contentName(im.bytes, im.mimeType) };
    const name = sharedName(im.uri);
    if (!name) return { ...im, name: null }; // someone else's URI: left alone
    const at = resolve(dir, dirname(file), im.uri);
    if (at !== resolve(texDir, name)) throw new Error(`${file}: ${im.uri} is not in ${texDir}`);
    const bytes = readFileSync(at);
    if (contentName(bytes, im.mimeType) !== name) throw new Error(`${file}: ${im.uri} does not hold the image its name says`);
    return { ...im, bytes, name };
  });
  return { json, bin, images };
}
const uses = new Map(), bytesOf = new Map();
for (const f of files) {
  for (const im of read(f).images) {
    if (!im.name) continue;
    if (!uses.has(im.name)) uses.set(im.name, new Set());
    uses.get(im.name).add(f); if (!bytesOf.has(im.name)) bytesOf.set(im.name, Buffer.from(im.bytes));
  }
}
const shared = sharedSet(uses, embedAll ? Infinity : 2);
const put = (path, bytes) => { writeFileSync(path + '.part', bytes); renameSync(path + '.part', path); };
if (shared.size) mkdirSync(texDir, { recursive: true });
let written = 0;
for (const name of shared) if (!existsSync(join(texDir, name))) { put(join(texDir, name), bytesOf.get(name)); written++; }
let rewritten = 0;
for (const f of files) {
  const { json, bin, images } = read(f), plan = planFile(f, images, shared);
  if (!plan.size) continue;
  const actions = new Map([...plan].map(([i, a]) => [i, a.uri ? a : { bytes: bytesOf.get(a.embed) }]));
  const r = rewriteGlb(json, bin, actions);
  put(join(dir, f), buildGlb(r.json, r.bin)); rewritten++;
}
let pruned = 0;
for (const f of texFiles()) if (!shared.has(f)) { rmSync(join(texDir, f)); pruned++; }
if (existsSync(texDir) && !texFiles().length) rmdirSync(texDir);
const texBytes = texFiles().reduce((s, f) => s + size(join(texDir, f)), 0);
const after = files.reduce((s, f) => s + size(join(dir, f)), 0) + texBytes;
console.log(`share images: ${files.length} tiles, ${shared.size} shared files (${(texBytes / 1e6).toFixed(2)} MB; ${written} new, ` +
  `${pruned} pruned), ${rewritten} tiles rewritten, ${(before / 1e6).toFixed(2)} -> ${(after / 1e6).toFixed(2)} MB`);
