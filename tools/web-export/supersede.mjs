// One campus, several sources: where an area of the scripted build owns the ground, take the other sources'
// ground out of their tiles, so two grounds never lie on top of each other. Rules come from
// blender/scripted/supersede.py (per area: footprint outline, and which meshes are ground there).
//   node supersede.mjs RULES.json MODELS_DIR
// For every area and every tile that is not a scripted-build tile:
//   clip  meshes: triangles wholly inside the footprint are removed; a triangle that straddles its edge, holds one
//         of its corners or is crossed by it is cut exactly where the outline crosses it (cut.mjs), split into four
//         first only where the outline turns inside it or crosses it with every corner inside (a notch): the old ground
//         ends at the footprint at its own height, a quantisation step (at least 2 cm) under the new ground's edge, so
//         no crack opens and nothing dips. On a coarse grid (the far field) a cut corner is stored at a grid point
//         inside the outline, never short of it (cut.mjs snapQuantized).
//         (`cut`, the piece size of the earlier version, stays in the rules' hash only.)
//   drop  meshes: triangles wholly inside the footprint are removed, nothing else changes
// Tiles done by the earlier version (straddlers kept whole, their inside corners lowered by `tuck` metres, which
// left a trench of 0 to `tuck` metres along the outside of the edge) are mended: those corners are raised back
// and the pieces cut as above. A primitive cut this way carries the rules' hash in its extras `cut` too.
// Far-field trees (far_trees.bin) inside the footprint are removed too: they are a scatter, not real trees.
// A primitive is marked in its extras once done (with a hash of each area's rules), so a second run leaves it
// alone, and a run with a changed footprint stops instead of leaving old holes or old ground. Geometry stays in its
// quantized form and is written back with the same meshopt filters, so a tile does not grow or lose precision.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { compactPrimitive, getBounds, joinPrimitives } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { readFileSync, writeFileSync, readdirSync, existsSync, appendFileSync } from 'node:fs';
import { crossings, cornersIn, edgesCross, outsidePart, ringDistance, snapQuantized, behind, planeLevel, splitEdge } from './cut.mjs';
import { keepShared, sharedRefs } from './tex.mjs';
import { pattern, region, cutVolume } from './volume.mjs';

const [rulesFile, dir] = process.argv.slice(2);
if (!rulesFile || !dir) { console.error('usage: node supersede.mjs RULES.json MODELS_DIR'); process.exit(2); }
const file = JSON.parse(readFileSync(rulesFile, 'utf8'));
const AREAS = file.areas ?? [file]; // one set of rules per area (a file with a single footprint is one area)
/** Even-odd test in the model frame (x east, y north). */
function inside(ring, x, y) {
  let hit = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const a = ring[i], b = ring[j];
    if ((a[1] > y) !== (b[1] > y) && x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])) hit = !hit;
  }
  return hit;
}

await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
const stale = new Set(), changedTiles = new Set(), KNOWN = new Set();
// Every area's hash first: a mark that is none of them is from rules that no longer exist.
// (an area's volumes join the hash only when it has some, so the marks of the areas with ground stay what they were)
const hashOf = rules => { let h = 2166136261; for (const c of JSON.stringify([rules.footprint, rules.clip, rules.drop ?? [], rules.tuck ?? 0.5, rules.cut ?? 0.6, ...(rules.volumes ? [rules.volumes] : [])])) h = Math.imul(h ^ c.charCodeAt(0), 16777619) >>> 0; return 'r' + h.toString(16); };
for (const rules of AREAS) KNOWN.add(hashOf(rules));
const areas = AREAS.filter(rules => !rules.skip && rules.footprint).map(rules => { // a skipped area's marks stay known, its ground stays
  // moved by a fraction of a millimetre, so that no corner of a ground mesh drawn on a round-metre grid lies exactly
  // on the outline (where the inside test and the edge crossings could disagree)
  const ring = rules.footprint.map(([x, y]) => [x + 1.37e-4, y + 2.71e-4]);
  const bx = [Math.min(...ring.map(p => p[0])), Math.min(...ring.map(p => p[1])), Math.max(...ring.map(p => p[0])), Math.max(...ring.map(p => p[1]))];
  return {
    name: rules.name ?? '', ring, bx, TUCK: rules.tuck ?? 0.5,
    CLIP: rules.clip.map(r => new RegExp(r)), DROP: (rules.drop ?? []).map(r => new RegExp(r)),
    // What a done primitive is marked with: a short hash of each area's rules it was done with. Removed triangles
    // cannot be put back, so a tile that was done with other rules (another footprint) must be exported again.
    RULES: hashOf(rules),
    within: (x, y) => x >= bx[0] && x <= bx[2] && y >= bx[1] && y <= bx[3] && inside(ring, x, y),
  };
});

// ---------- volumes: an area that owns no ground (a building the scripted build rebuilds) ----------
// Per volume, in order: a `ring` takes out the other sources' triangles inside it (at any height, or only above
// `above` and at or below `below`, model metres: a door through another model's wall), cut exactly at the ring's walls and at the level (volume.mjs), except primitives whose
// 'mesh name material name' matches `keep`; instanced nodes whose origin lies inside lose those instances. `meshes`
// drops meshes of exactly those names, wherever they are. Done primitives and nodes carry the area's hash in their
// extras `superseded`, and so does the tile's scene, so a changed volume stops the run like a changed footprint.
const volumeAreas = AREAS.filter(rules => !rules.skip && rules.volumes).map(rules => ({
  name: rules.name ?? '', RULES: hashOf(rules),
  vols: rules.volumes.map(v => ({
    name: v.name, meshes: new Set(v.meshes ?? []), reg: v.ring ? region(v.ring) : null,
    above: v.above ?? null, below: v.below ?? null, keep: (v.keep ?? []).map(pattern),
  })),
}));
// metres: a corner the outline cut in a coarsely quantised mesh is stored at least this far inside the outline
const MARGIN = 0.01;
// metres outside the outline within which a corner the earlier version lowered can lie now (see `pit`)
const MEND_NEAR = 0.1;
// metres between grid points from which the cut pieces get exact positions (the far field), and how far a cut corner
// of those is pulled along its edge under the new ground (a hair, so the two edges overlap and no pinhole shows)
const EXACT = 0.05, EXACT_OVER = 0.005;

/** A primitive of the cut pieces `tris` (corner indices into `prim`, which holds the added corners already): the same
 * material and attributes, positions as floats, the corners on the outline at their exact place (`exactPos`, by added
 * index k = corner - n). Its extras say `edge`. */
function edgePrimitive(doc, prim, tris, n, exactPos, extras) {
  const used = [...new Set(tris)], at = new Map(used.map((v, i) => [v, i]));
  const ep = doc.createPrimitive().setMode(4).setMaterial(prim.getMaterial());
  const buf = prim.getAttribute('POSITION').getBuffer(), e = [];
  for (const sem of prim.listSemantics()) {
    const a = prim.getAttribute(sem), size = a.getElementSize(), pos = sem === 'POSITION';
    const arr = pos ? new Float32Array(used.length * size) : new (a.getArray().constructor)(used.length * size);
    used.forEach((v, i) => {
      if (pos) arr.set(v >= n && exactPos.has(v - n) ? exactPos.get(v - n) : a.getElement(v, e), i * size);
      else arr.set(a.getArray().subarray(v * size, v * size + size), i * size);
    });
    ep.setAttribute(sem, doc.createAccessor().setType(a.getType()).setArray(arr).setNormalized(pos ? false : a.getNormalized()).setBuffer(buf));
  }
  const ix = tris.map(v => at.get(v));
  ep.setIndices(doc.createAccessor().setType('SCALAR').setArray(used.length > 65535 ? new Uint32Array(ix) : new Uint16Array(ix)).setBuffer(buf));
  return ep.setExtras({ ...extras, edge: 1 });
}

/** One primitive of cut pieces per mesh and material: every area that cut a far field added one. */
function joinEdges(doc) {
  for (const mesh of doc.getRoot().listMeshes()) {
    const groups = new Map();
    for (const p of mesh.listPrimitives()) if (p.getExtras().edge) groups.set(p.getMaterial(), [...(groups.get(p.getMaterial()) ?? []), p]);
    for (const prims of groups.values()) {
      if (prims.length < 2) continue;
      const marks = k => [...new Set(prims.flatMap(p => (p.getExtras()[k] ?? '').split(' ').filter(Boolean)))].join(' ');
      const joined = joinPrimitives(prims).setExtras({ ...prims[0].getExtras(), superseded: marks('superseded'), cut: marks('cut'), edge: 1 });
      for (const p of prims) { mesh.removePrimitive(p); p.dispose(); }
      mesh.addPrimitive(joined);
    }
  }
}
const marksOf = x => (x.getExtras().superseded ?? '').split(' ').filter(Boolean);
const mark = (x, RULES) => { const m = marksOf(x); if (!m.includes(RULES)) x.setExtras({ ...x.getExtras(), superseded: [...m, RULES].join(' ') }); };
// what each volume took, per 'mesh material' label: VOLUME_STATS=FILE appends one JSON line per changed tile
const tally = (st, vol, label, key, n) => {
  const t = (st[vol] ??= {})[label] ??= { removed: 0, cut: 0, instances: 0, whole: 0 };
  t[key] += n;
};
// model frame (x east, y north, z up) of a point in a node's space: viewer y is up, viewer z is minus north
const toModel = (w, p) => [w[0] * p[0] + w[4] * p[1] + w[8] * p[2] + w[12], -(w[2] * p[0] + w[6] * p[1] + w[10] * p[2] + w[14]), w[1] * p[0] + w[5] * p[1] + w[9] * p[2] + w[13]];
const boxMeets = (lo, hi, bx) => !(hi[0] < bx[0] || lo[0] > bx[2] || hi[1] < bx[1] || lo[1] > bx[3]);

/** A primitive's new corners and triangles: every attribute gets the added corners as weighted means. */
function rewrite(prim, n, added, keep) {
  const idx = prim.getIndices(), total = n + added.length, olds = [idx];
  for (const sem of prim.listSemantics()) {
    const old = prim.getAttribute(sem), copy = old.clone(), size = old.getElementSize();
    if (added.length) { const arr = new (old.getArray().constructor)(total * size); arr.set(old.getArray()); copy.setArray(arr); }
    const e = [], sum = new Array(size);
    for (let k = 0; k < added.length; k++) {
      sum.fill(0);
      for (const [i, wgt] of added[k]) { copy.getElement(i, e); for (let q = 0; q < size; q++) sum[q] += e[q] * wgt; }
      copy.setElement(n + k, sum);
    }
    prim.setAttribute(sem, copy); olds.push(old);
  }
  prim.setIndices(idx.clone().setArray(total > 65535 ? new Uint32Array(keep) : new Uint16Array(keep)));
  for (const old of olds) if (!old.listParents().some(x => x.propertyType !== 'Root')) old.dispose();
  compactPrimitive(prim);
}

/** Instances of an instanced node whose origin lies in a volume go; returns how many went. */
function dropInstances(node, w, test) {
  const inst = node.getExtension('EXT_mesh_gpu_instancing'), tr = inst.getAttribute('TRANSLATION');
  const count = inst.listAttributes()[0]?.getCount() ?? 0, p = [0, 0, 0], keepRows = [];
  for (let i = 0; i < count; i++) {
    if (tr) tr.getElement(i, p); else p.fill(0);
    if (!test(toModel(w, p))) keepRows.push(i);
  }
  if (keepRows.length === count) return 0;
  if (!keepRows.length) { node.setMesh(null); node.setExtension('EXT_mesh_gpu_instancing', null); return count; }
  for (const sem of inst.listSemantics()) {
    const a = inst.getAttribute(sem), size = a.getElementSize(), src = a.getArray();
    const arr = new src.constructor(keepRows.length * size);
    keepRows.forEach((r, k) => arr.set(src.subarray(r * size, r * size + size), k * size));
    inst.setAttribute(sem, a.clone().setArray(arr));
    if (!a.listParents().some(x => x.propertyType !== 'Root')) a.dispose();
  }
  return count - keepRows.length;
}

function applyVolumes(doc, f, { name, RULES, vols }) {
  const scene = doc.getRoot().getDefaultScene() ?? doc.getRoot().listScenes()[0];
  if (scene && marksOf(scene).some(m => !KNOWN.has(m))) { stale.add(f); return false; }
  let changed = false;
  const st = {};
  for (const node of doc.getRoot().listNodes()) {
    let mesh = node.getMesh();
    if (!mesh) continue;
    const w = node.getWorldMatrix(), mname = mesh.getName();
    const label = p => `${mname} ${p?.getMaterial()?.getName() ?? ''}`;
    for (const v of vols) if (v.meshes.has(mname) && node.getMesh()) {
      for (const p of mesh.listPrimitives()) tally(st, v.name, label(p), 'whole', (p.getIndices()?.getCount() ?? 0) / 3);
      node.setMesh(null); changed = true;
    }
    if (!node.getMesh()) continue;
    if (marksOf(node).some(m => !KNOWN.has(m))) { stale.add(f); continue; }
    if (node.getExtension('EXT_mesh_gpu_instancing')) {
      const labels = mesh.listPrimitives().map(label).join(' ');
      for (const v of vols) {
        if (!v.reg || v.keep.some(r => r.test(labels)) || !node.getMesh()) continue;
        const n = dropInstances(node, w, ([x, y, z]) => v.reg.within(x, y) && (v.above === null || z > v.above) && (v.below === null || z <= v.below));
        if (n) { tally(st, v.name, labels, 'instances', n); mark(node, RULES); changed = true; }
      }
      continue;
    }
    const rings = vols.filter(v => v.reg);
    if (!rings.length) continue;
    // a mesh that two nodes share is cut for this node's place only: it gets a copy of its own first
    const { min, max } = getBounds(node), lo = [min[0], -max[2]], hi = [max[0], -min[2]];
    if (!rings.some(v => boxMeets(lo, hi, v.reg.bx))) continue;
    if (mesh.listParents().filter(x => x.propertyType === 'Node').length > 1) {
      const own = doc.createMesh(mname);
      for (const p of mesh.listPrimitives()) own.addPrimitive(p.clone());
      node.setMesh(own); mesh = own;
    }
    for (const prim of mesh.listPrimitives()) {
      if (prim.getMode() !== 4 || !prim.getIndices()) continue;
      const done = marksOf(prim);
      if (done.some(m => !KNOWN.has(m))) { stale.add(f); continue; }
      if (done.includes(RULES)) continue;
      const lab = label(prim), todo = rings.filter(v => !v.keep.some(r => r.test(lab)));
      if (!todo.length) continue;
      const pos = prim.getAttribute('POSITION'), n = pos.getCount(), p = [0, 0, 0];
      const X = new Array(n), Y = new Array(n), Z = new Array(n);
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      for (let i = 0; i < n; i++) {
        pos.getElement(i, p); [X[i], Y[i], Z[i]] = toModel(w, p);
        x0 = Math.min(x0, X[i]); x1 = Math.max(x1, X[i]); y0 = Math.min(y0, Y[i]); y1 = Math.max(y1, Y[i]);
      }
      const pts = { X, Y, Z }, added = [];
      let tris = Array.from(prim.getIndices().getArray()), any = false;
      for (const v of todo) {
        if (!boxMeets([x0, y0], [x1, y1], v.reg.bx)) continue;
        const r = cutVolume(pts, added, tris, v.reg, v.above, v.below);
        if (!r.removed && !r.cut) continue;
        tally(st, v.name, lab, 'removed', r.removed); tally(st, v.name, lab, 'cut', r.cut);
        tris = r.keep; any = true;
      }
      if (!any) continue;
      changed = true;
      if (!tris.length) { mesh.removePrimitive(prim); prim.dispose(); continue; }
      rewrite(prim, n, added, tris);
      mark(prim, RULES);
    }
    if (!mesh.listPrimitives().length) node.setMesh(null);
  }
  if (!changed) return false;
  if (scene) mark(scene, RULES);
  for (const [v, labels] of Object.entries(st)) {
    const s = Object.values(labels).reduce((a, b) => ({ removed: a.removed + b.removed, cut: a.cut + b.cut, instances: a.instances + b.instances, whole: a.whole + b.whole }), { removed: 0, cut: 0, instances: 0, whole: 0 });
    console.log(`supersede ${name}/${v} ${f}: removed ${s.removed} triangles, cut ${s.cut} at the ring or level, ${s.instances} instances, ${s.whole} triangles of whole meshes`);
  }
  if (process.env.VOLUME_STATS) appendFileSync(process.env.VOLUME_STATS, JSON.stringify({ tile: f, area: name, volumes: st }) + '\n');
  return true;
}

// Every tile, read once: an object is filed under the tile that holds its centre, and a far-field ground filed under
// one tile reaches a kilometre and more past it, so no tile can be left out by its name.
for (const f of readdirSync(dir).filter(f => f.endsWith('.glb') && !f.startsWith('sw_')).sort()) {
  const doc = await io.read(`${dir}/${f}`);
  let dirty = false;
  for (const { name, ring, bx, TUCK, CLIP, DROP, RULES, within } of areas) {
  let removed = 0, cutN = 0, mended = 0, removedAll = 0;
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh();
    if (!mesh || node.getExtension('EXT_mesh_gpu_instancing')) continue;
    const w = node.getWorldMatrix();
    // raising by TUCK along world up (viewer +Y), written in the mesh's own space: inverse(rotation * scale) * (0, TUCK, 0)
    // (undoes the earlier version's lowering)
    const s2 = k => (w[k] * w[k] + w[k + 1] * w[k + 1] + w[k + 2] * w[k + 2]) || 1;
    const local = p => toModel(w, p), keepIn = (x, y) => within(x, y) && ringDistance(ring, x, y) >= MARGIN;
    const up = [TUCK * w[1] / s2(0), TUCK * w[5] / s2(4), TUCK * w[9] / s2(8)];
    for (const prim of mesh.listPrimitives()) {
      const label = `${mesh.getName()} ${prim.getMaterial()?.getName() ?? ''}`;
      const mode = DROP.some(r => r.test(label)) ? 'drop' : CLIP.some(r => r.test(label)) ? 'clip' : null;
      if (!mode || prim.getMode() !== 4) continue;
      const done = (prim.getExtras().superseded ?? '').split(' ').filter(Boolean);
      if (done.some(m => !KNOWN.has(m))) { stale.add(f); continue; }
      const cutDone = (prim.getExtras().cut ?? '').split(' ').filter(Boolean);
      // done by the earlier version: its trench is mended below; done by this one: nothing to do
      const mend = done.includes(RULES) && mode === 'clip' && !cutDone.includes(RULES);
      if (done.includes(RULES) && !mend) continue;
      const src = prim.getAttribute('POSITION'), idx = prim.getIndices();
      if (!src || !idx) continue;
      // a cut corner is a new vertex, rounded to the mesh's quantisation grid: pull it under the new ground by
      // at least one step so rounding cannot open a crack (and a T-junction with the new edge cannot show). Pulled
      // along its edge, a corner moves less than that across the outline where the edge crosses it at a slant, and
      // the pull stops at 15 cm while the north model's far field has a grid of 0.38 m: rounded to the nearest grid
      // point, its cut edge ended up to a quarter metre short of the outline (a crack down to the lower skirt).
      // On a grid of EXACT or more (the far field: the skirt's 6 cm, the north model's 0.38 m) the pieces the outline
      // cut go to a primitive of their own with exact (float) positions, cut on the outline: any grid point inside it
      // left far field standing over the new ground's edge where the far field stands higher (shards up to 0.37 m
      // high and half a metre into the lawn in sw17), any outside it a crack. On a grid of a centimetre or more a corner
      // on the outline is stored at the nearest grid point at least MARGIN inside it (snapQuantized); its height is
      // rounded as before, so a corner that rounding left inside does not move at all. A primitive the earlier version
      // cut (southwest's marks in the tiles restored from fc1401b) is mended (its lowered corners raised back) and then
      // cut the same way: sw17 cut its far field on the grid as sw16 did, and left 16 m² of skirt standing up to 0.68 m
      // over the south-west area's ground (0.01 m² on scratch copies of the fc1401b tiles cut this way)
      const DIV = { 5120: 127, 5121: 255, 5122: 32767, 5123: 65535 }[src.getComponentType()];
      const STEP = DIV && src.getNormalized() ? Math.sqrt(s2(0)) / DIV : 0, EXACT_CUT = STEP >= EXACT, SNAP = !EXACT_CUT && STEP >= MARGIN;
      const PULL = Math.min(0.15, Math.max(0.02, STEP)), OVER = EXACT_CUT || prim.getExtras().edge ? EXACT_OVER : PULL;
      const n = src.getCount(), p = [0, 0, 0];
      // model-frame position of every corner (viewer z is minus model y), and whether it is inside
      const wx = new Float64Array(n), wy = new Float64Array(n), isIn = Array.from({ length: n }, () => 0);
      const loc = EXACT_CUT ? [] : null; // node-space corners, for the grid an added midpoint is stored on
      let any = false;
      for (let i = 0; i < n; i++) {
        src.getElement(i, p);
        if (loc) loc.push(p.slice());
        wx[i] = w[0] * p[0] + w[4] * p[1] + w[8] * p[2] + w[12]; wy[i] = -(w[2] * p[0] + w[6] * p[1] + w[10] * p[2] + w[14]);
        if (within(wx[i], wy[i])) { isIn[i] = 1; any = true; }
      }
      // no corner inside: its triangles can still cover the footprint, if any of them reaches its box
      if (!any) {
        let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
        for (let i = 0; i < n; i++) { x0 = Math.min(x0, wx[i]); x1 = Math.max(x1, wx[i]); y0 = Math.min(y0, wy[i]); y1 = Math.max(y1, wy[i]); }
        if (x1 < bx[0] || x0 > bx[2] || y1 < bx[1] || y0 > bx[3]) continue;
      }
      const before = removed + cutN;
      // corners added by cutting, numbered after the original ones: each a weighted mean of earlier corners,
      // [[corner, weight], ...] (an edge's midpoint, a point where the outline crosses an edge, an outline corner)
      // onLine: added corners on the outline, each with the outline corner it stands for (-1: a crossing on a run) and
      // the triangle it was cut from
      const added = [], ax = [], ay = [], memo = new Map(), onLine = new Map();
      const X = i => (i < n ? wx[i] : ax[i - n]), Y = i => (i < n ? wy[i] : ay[i - n]);
      const add = (key, parents, inside, line = null) => {
        let m = key === null ? undefined : memo.get(key);
        if (m === undefined) {
          m = n + added.length; added.push(parents);
          if (line !== null) onLine.set(m - n, line);
          if (loc) {
            // with exact cut pieces, a midpoint stays on the grid (the rest of the far field shares it), and the outline
            // is cut where it crosses the edges as stored: cut on the unrounded edge, a corner landed up to 0.2 m off it
            const q = [0, 1, 2].map(c => parents.reduce((s, [i, k]) => s + loc[i][c] * k, 0));
            const r = line === null ? q.map(v => Math.round(v * DIV) / DIV) : q;
            loc.push(r);
            const [mx, my] = toModel(w, r);
            ax.push(mx); ay.push(my);
            isIn[m] = line === null ? (within(mx, my) ? 1 : 0) : 0;
          } else {
            ax.push(parents.reduce((s, [i, k]) => s + X(i) * k, 0)); ay.push(parents.reduce((s, [i, k]) => s + Y(i) * k, 0));
            isIn[m] = inside ? 1 : 0;
          }
          if (key !== null) memo.set(key, m);
        }
        return m;
      };
      const pair = (a, b) => (a < b ? a * 4294967296 + b : b * 4294967296 + a);
      const mid = (a, b) => add('m' + pair(a, b), [[a, 0.5], [b, 0.5]], within((X(a) + X(b)) / 2, (Y(a) + Y(b)) / 2));
      // the crossing on an edge is found from its inside corner, so the two triangles on the edge share it
      const cross = (i, o, t, tri) => add('x' + i * 4294967296 + o, [[i, 1 - t], [o, t]], false, { corner: -1, tri });
      const I = idx.getArray();
      let keep = [];
      const P = i => [X(i), Y(i)];
      // straddling edges crossed once, other edges not at all: the piece can be cut with one run of the outline
      const plain = (a, b, c) => [[a, b], [b, c], [c, a]].every(([u, v]) => crossings(X(u), Y(u), X(v), Y(v), ring).length === (isIn[u] !== isIn[v] ? 1 : 0));
      // A triangle wholly inside goes. One that the outline crosses keeps exactly its part outside the outline; where
      // the outline turns inside it (or crosses one edge twice) it is cut into four first, again and again.
      const visit = (a, b, c, depth) => {
        const k = isIn[a] + isIn[b] + isIn[c];
        const away = Math.max(X(a), X(b), X(c)) < bx[0] || Math.min(X(a), X(b), X(c)) > bx[2] ||
          Math.max(Y(a), Y(b), Y(c)) < bx[1] || Math.min(Y(a), Y(b), Y(c)) > bx[3];
        const corners = mode === 'clip' && !away ? cornersIn(ring, P(a), P(b), P(c)) : [];
        // all corners inside and no outline corner inside: a notch of the outline can still run through it (a far-field
        // triangle 10 m across over the Village's notch at (-200, 722) went whole, leaving a hole down to nothing)
        if (!corners.length && k === 3 && (away || mode !== 'clip' || !edgesCross(ring, [P(a), P(b), P(c)]))) { removed++; return; }
        // all corners outside and no outline corner inside: a band of footprint can still cross it
        if (!corners.length && k === 0 && (away || mode !== 'clip' || !edgesCross(ring, [P(a), P(b), P(c)]))) { keep.push(a, b, c); return; }
        if (mode === 'drop') { if (k === 3) removed++; else keep.push(a, b, c); return; }
        const simple = k > 0 && k < 3 && corners.length <= 1 && plain(a, b, c);
        // An exact cut needs no small pieces: split only where the outline turns inside a piece or crosses an edge
        // twice, down to 5 cm (round an outline corner that lies on an edge or a corner of the ground's own mesh,
        // pieces never become simple)
        const longest = Math.max(Math.hypot(X(a) - X(b), Y(a) - Y(b)), Math.hypot(X(b) - X(c), Y(b) - Y(c)), Math.hypot(X(c) - X(a), Y(c) - Y(a)));
        if (depth < 16 && longest > 0.05 && !simple) {
          const ab = mid(a, b), bc = mid(b, c), ca = mid(c, a);
          visit(a, ab, ca, depth + 1); visit(ab, b, bc, depth + 1); visit(ca, bc, c, depth + 1); visit(ab, bc, ca, depth + 1);
          return;
        }
        if (!simple) { if (k === 3) removed++; else keep.push(a, b, c); return; } // a few centimetres across by now
        const ids = [a, b, c], tri = ids.map(P);
        const at = corners.length ? { index: corners[0], at: ring[corners[0]] } : null;
        const part = outsidePart(ring, tri, ids.map(i => isIn[i] === 1), at, OVER);
        const vs = part.map(q => {
          if (q.kind === 'corner') return ids[q.i];
          if (q.kind === 'cross') {
            const [i, o] = [ids[q.edge[0]], ids[q.edge[1]]], len = Math.hypot(X(o) - X(i), Y(o) - Y(i)) || 1;
            const v = cross(i, o, q.t, ids), tz = Math.max(0, q.t + (OVER - PULL) / len);
            onLine.get(v - n).height = [[i, 1 - tz], [o, tz]]; // where sw16 read its height: see the write below
            return v;
          }
          // the outline corner: barycentric weights of the piece's corners
          const [[x1, y1], [x2, y2], [x3, y3]] = tri, d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3);
          const l1 = ((y2 - y3) * (q.x - x3) + (x3 - x2) * (q.y - y3)) / d, l2 = ((y3 - y1) * (q.x - x3) + (x1 - x3) * (q.y - y3)) / d;
          return add(null, [[a, l1], [b, l2], [c, 1 - l1 - l2]], false, { corner: q.index, tri: ids });
        });
        // a fan from the outline corner (the part is star-shaped round it) or from any corner of a convex part
        const s0 = Math.max(0, part.findIndex(q => q.kind === 'ring'));
        for (let j = 1; j < vs.length - 1; j++) keep.push(vs[s0], vs[(s0 + j) % vs.length], vs[(s0 + j + 1) % vs.length]);
        cutN++;
      };
      for (let t = 0; t < I.length; t += 3) visit(I[t], I[t + 1], I[t + 2], 0);
      if (removed + cutN === before && !mend) continue; // it only came near
      if (!keep.length) { mesh.removePrimitive(prim); prim.dispose(); removedAll++; continue; }
      // corners the earlier version lowered that lie on the outline can read as outside it now (within a millimetre:
      // a row of skirt corners at (-421.8, -360.6) by southwest's edge stood 0.48 m low, and the exact cut ended the
      // far field 0.25 m under southwest's ground there). A corner within MEND_NEAR outside the outline is raised back
      // too where it stands TUCK (give or take 40 %) under the highest corner it shares a triangle with that lies
      // further out (and so was never lowered)
      const pit = new Uint8Array(n);
      if (mend && STEP >= EXACT) { // the far field only: the main and north models' own ground is fine and steep in places
        const zOf = i => { src.getElement(i, p); return toModel(w, p)[2]; };
        const near = i => !isIn[i] && ringDistance(ring, wx[i], wy[i]) <= MEND_NEAR, high = new Float64Array(n).fill(-Infinity);
        for (let t = 0; t < I.length; t += 3) for (let k = 0; k < 3; k++) {
          const i = I[t + k];
          if (!near(i)) continue;
          for (const j of [I[t + (k + 1) % 3], I[t + (k + 2) % 3]]) if (!isIn[j] && !near(j)) high[i] = Math.max(high[i], zOf(j));
        }
        for (let i = 0; i < n; i++) {
          const drop = high[i] - (Number.isFinite(high[i]) ? zOf(i) : 0);
          if (Number.isFinite(high[i]) && drop > 0.6 * TUCK && drop < 1.4 * TUCK) pit[i] = 1;
        }
      }
      // accessors can be shared between primitives: edit copies, and drop the originals nobody uses any more.
      // Every attribute gets the added corners, each the weighted mean of its parents (parents come first).
      const total = n + added.length, olds = [idx], exactPos = new Map();
      for (const sem of prim.listSemantics()) {
        const old = prim.getAttribute(sem), copy = old.clone(), size = old.getElementSize();
        if (added.length) {
          const arr = new (old.getArray().constructor)(total * size); arr.set(old.getArray()); copy.setArray(arr);
        }
        if (sem === 'POSITION' && mend) {
          // the earlier version lowered every inside corner it kept by TUCK: put them back first
          for (let i = 0; i < n; i++) if (isIn[i] || pit[i]) { copy.getElement(i, p); copy.setElement(i, [p[0] + up[0], p[1] + up[1], p[2] + up[2]]); mended++; }
        }
        const e = [], sum = new Array(size);
        for (let k = 0; k < added.length; k++) {
          sum.fill(0);
          for (const [i, wgt] of added[k]) { copy.getElement(i, e); for (let q = 0; q < size; q++) sum[q] += e[q] * wgt; }
          copy.setElement(n + k, sum);
          if (sem === 'POSITION' && EXACT_CUT && onLine.has(k)) {
            // the place is exact; the height is the one sw16 stored there (read PULL back along the edge, rounded to the
            // grid): the edge heights of descent, Lot 60 and Normal Avenue were read from tiles cut that way, and on
            // the north model's 0.38 m height steps an exact height lay up to 0.19 m off them
            const x = sum.slice(), rise = [w[1], w[5], w[9]].map(Math.abs), upAx = rise.indexOf(Math.max(...rise));
            const h = onLine.get(k).height;
            const z = h ? h.reduce((t, [i, wgt]) => t + copy.getElement(i, e)[upAx] * wgt, 0) : x[upAx];
            x[upAx] = Math.round(z * DIV) / DIV;
            exactPos.set(k, x);
          }
          if (sem === 'POSITION' && SNAP && onLine.has(k)) {
            const { corner, tri } = onLine.get(k);
            const keep = corner < 0 ? keepIn : (x, y) => keepIn(x, y) && behind(ring, corner, x, y) >= MARGIN;
            // the cut triangle's own plane gives the height where the corner moves (up: the axis most of model z)
            const [p0, p1, p2] = tri.map(i => copy.getElement(i, []));
            const rise = [w[1], w[5], w[9]].map(Math.abs), up = rise.indexOf(Math.max(...rise));
            copy.getArray().set(snapQuantized(sum, DIV, local, keep, 3, planeLevel(p0, p1, p2, up)), (n + k) * size);
          }
        }
        prim.setAttribute(sem, copy); olds.push(old);
      }
      const marks = done.includes(RULES) ? done : [...done, RULES];
      const extras = { ...prim.getExtras(), superseded: marks.join(' '), ...(mode === 'clip' ? { cut: [...cutDone, RULES].join(' ') } : {}) };
      if (EXACT_CUT) {
        const { rest, edge } = splitEdge(keep, n, onLine);
        keep = rest;
        if (edge.length) mesh.addPrimitive(edgePrimitive(doc, prim, edge, n, exactPos, extras));
      }
      prim.setIndices(idx.clone().setArray(total > 65535 ? new Uint32Array(keep) : new Uint16Array(keep)));
      for (const old of olds) if (!old.listParents().some(x => x.propertyType !== 'Root')) old.dispose();
      if (!keep.length) { mesh.removePrimitive(prim); prim.dispose(); continue; }
      compactPrimitive(prim); // drops the corners no triangle uses any more; the index buffer compresses badly with gaps
      prim.setExtras(extras);
    }
    if (!mesh.listPrimitives().length) node.setMesh(null);
  }
  if (!removed && !cutN && !mended) continue;
  dirty = true;
  console.log(`supersede ${name} ${f}: removed ${removed} triangles (${removedAll} whole primitives), cut ${cutN} at the outline, mended ${mended} corners`);
  }
  for (const va of volumeAreas) if (applyVolumes(doc, f, va)) dirty = true;
  if (!dirty) continue;
  joinEdges(doc);
  for (const m of doc.getRoot().listMeshes()) if (!m.listPrimitives().length) m.dispose();
  for (const a of doc.getRoot().listAccessors()) if (!a.listParents().some(x => x.propertyType !== 'Root')) a.dispose();
  // same encoding as `gltf-transform optimize --compress meshopt` wrote
  doc.getRoot().listExtensionsUsed().find(e => e.extensionName === 'EXT_meshopt_compression')?.setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.FILTER });
  // images the tile shares with others (models/main/tex/) stay outside it: io.write would embed them
  const path = `${dir}/${f}`;
  writeFileSync(path, keepShared(await io.writeBinary(doc), sharedRefs(doc.getRoot().listTextures().map(t => t.getURI()), path, path)));
  changedTiles.add(f);
}
// far-field trees: [x, y, z, crown radius, height] in viewer axes
const ft = `${dir}/far_trees.bin`;
// (and inside a volume's ring that keeps nothing and has no level)
const treeRings = volumeAreas.flatMap(a => a.vols.filter(v => v.reg && v.above === null && v.below === null && !v.keep.length).map(v => v.reg));
for (const { within } of [...areas, ...treeRings]) if (existsSync(ft)) {
  const raw = readFileSync(ft); // a small file's Buffer is a view into a shared pool: copy exactly its bytes
  const a = new Float32Array(raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.length - (raw.length % 4))), keep = [];
  for (let i = 0; i + 4 < a.length; i += 5) if (!within(a[i], -a[i + 2])) keep.push(a[i], a[i + 1], a[i + 2], a[i + 3], a[i + 4]);
  if (keep.length !== a.length) { writeFileSync(ft, Buffer.from(new Float32Array(keep).buffer)); console.log(`supersede far_trees.bin: removed ${(a.length - keep.length) / 5} trees`); }
}
if (stale.size) {
  console.error(`supersede: ${[...stale].join(' ')} were done with other rules (the footprint or the patterns changed). ` +
    'Export those tiles again (or restore them from before the scripted build), then run this again.');
  process.exit(1);
}
// the caller rebuilds the far versions (lod/) of these tiles
console.log('CHANGED', [...changedTiles].join(' '));
