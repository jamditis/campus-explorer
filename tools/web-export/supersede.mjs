// One campus, several sources: where an area of the scripted build owns the ground, take the other sources'
// ground out of their tiles, so two grounds never lie on top of each other. Rules come from
// blender/scripted/supersede.py (per area: footprint outline, and which meshes are ground there).
//   node supersede.mjs RULES.json MODELS_DIR
// For every area and every tile that is not a scripted-build tile:
//   clip  meshes: triangles wholly inside the footprint are removed; a triangle that straddles its edge, holds one
//         of its corners or is crossed by it is cut exactly where the outline crosses it (cut.mjs), split into four
//         first only where the outline turns inside it: the old ground ends at the footprint at its own height, a
//         quantisation step (at least 2 cm) under the new ground's edge, so no crack opens and nothing dips.
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
import { compactPrimitive } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { crossings, cornersIn, edgesCross, outsidePart } from './cut.mjs';

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
const hashOf = rules => { let h = 2166136261; for (const c of JSON.stringify([rules.footprint, rules.clip, rules.drop ?? [], rules.tuck ?? 0.5, rules.cut ?? 0.6])) h = Math.imul(h ^ c.charCodeAt(0), 16777619) >>> 0; return 'r' + h.toString(16); };
for (const rules of AREAS) KNOWN.add(hashOf(rules));
const areas = AREAS.filter(rules => !rules.skip).map(rules => { // a skipped area's marks stay known, its ground stays
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
      // at least one step so rounding cannot open a crack (and a T-junction with the new edge cannot show)
      const DIV = { 5120: 127, 5121: 255, 5122: 32767, 5123: 65535 }[src.getComponentType()];
      const OVER = Math.min(0.15, Math.max(0.02, DIV && src.getNormalized() ? Math.sqrt(s2(0)) / DIV : 0));
      const n = src.getCount(), p = [0, 0, 0];
      // model-frame position of every corner (viewer z is minus model y), and whether it is inside
      const wx = new Float64Array(n), wy = new Float64Array(n), isIn = Array.from({ length: n }, () => 0);
      let any = false;
      for (let i = 0; i < n; i++) {
        src.getElement(i, p);
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
      const added = [], ax = [], ay = [], memo = new Map();
      const X = i => (i < n ? wx[i] : ax[i - n]), Y = i => (i < n ? wy[i] : ay[i - n]);
      const add = (key, parents, inside) => {
        let m = key === null ? undefined : memo.get(key);
        if (m === undefined) {
          m = n + added.length; added.push(parents);
          ax.push(parents.reduce((s, [i, k]) => s + X(i) * k, 0)); ay.push(parents.reduce((s, [i, k]) => s + Y(i) * k, 0));
          isIn[m] = inside ? 1 : 0;
          if (key !== null) memo.set(key, m);
        }
        return m;
      };
      const pair = (a, b) => (a < b ? a * 4294967296 + b : b * 4294967296 + a);
      const mid = (a, b) => add('m' + pair(a, b), [[a, 0.5], [b, 0.5]], within((X(a) + X(b)) / 2, (Y(a) + Y(b)) / 2));
      // the crossing on an edge is found from its inside corner, so the two triangles on the edge share it
      const cross = (i, o, t) => add('x' + i * 4294967296 + o, [[i, 1 - t], [o, t]], false);
      const I = idx.getArray(), keep = [];
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
        if (!corners.length && k === 3) { removed++; return; }
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
          if (q.kind === 'cross') return cross(ids[q.edge[0]], ids[q.edge[1]], q.t);
          // the outline corner: barycentric weights of the piece's corners
          const [[x1, y1], [x2, y2], [x3, y3]] = tri, d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3);
          const l1 = ((y2 - y3) * (q.x - x3) + (x3 - x2) * (q.y - y3)) / d, l2 = ((y3 - y1) * (q.x - x3) + (x1 - x3) * (q.y - y3)) / d;
          return add(null, [[a, l1], [b, l2], [c, 1 - l1 - l2]], false);
        });
        // a fan from the outline corner (the part is star-shaped round it) or from any corner of a convex part
        const s0 = Math.max(0, part.findIndex(q => q.kind === 'ring'));
        for (let j = 1; j < vs.length - 1; j++) keep.push(vs[s0], vs[(s0 + j) % vs.length], vs[(s0 + j + 1) % vs.length]);
        cutN++;
      };
      for (let t = 0; t < I.length; t += 3) visit(I[t], I[t + 1], I[t + 2], 0);
      if (removed + cutN === before && !mend) continue; // it only came near
      if (!keep.length) { mesh.removePrimitive(prim); prim.dispose(); removedAll++; continue; }
      // accessors can be shared between primitives: edit copies, and drop the originals nobody uses any more.
      // Every attribute gets the added corners, each the weighted mean of its parents (parents come first).
      const total = n + added.length, olds = [idx];
      for (const sem of prim.listSemantics()) {
        const old = prim.getAttribute(sem), copy = old.clone(), size = old.getElementSize();
        if (added.length) {
          const arr = new (old.getArray().constructor)(total * size); arr.set(old.getArray()); copy.setArray(arr);
        }
        if (sem === 'POSITION' && mend) {
          // the earlier version lowered every inside corner it kept by TUCK: put them back first
          for (let i = 0; i < n; i++) if (isIn[i]) { copy.getElement(i, p); copy.setElement(i, [p[0] + up[0], p[1] + up[1], p[2] + up[2]]); mended++; }
        }
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
      compactPrimitive(prim); // drops the corners no triangle uses any more; the index buffer compresses badly with gaps
      const marks = done.includes(RULES) ? done : [...done, RULES];
      prim.setExtras({ ...prim.getExtras(), superseded: marks.join(' '), ...(mode === 'clip' ? { cut: [...cutDone, RULES].join(' ') } : {}) });
    }
    if (!mesh.listPrimitives().length) node.setMesh(null);
  }
  if (!removed && !cutN && !mended) continue;
  dirty = true;
  console.log(`supersede ${name} ${f}: removed ${removed} triangles (${removedAll} whole primitives), cut ${cutN} at the outline, mended ${mended} corners`);
  }
  if (!dirty) continue;
  for (const m of doc.getRoot().listMeshes()) if (!m.listPrimitives().length) m.dispose();
  for (const a of doc.getRoot().listAccessors()) if (!a.listParents().some(x => x.propertyType !== 'Root')) a.dispose();
  // same encoding as `gltf-transform optimize --compress meshopt` wrote
  doc.getRoot().listExtensionsUsed().find(e => e.extensionName === 'EXT_meshopt_compression')?.setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.FILTER });
  await io.write(`${dir}/${f}`, doc);
  changedTiles.add(f);
}
// far-field trees: [x, y, z, crown radius, height] in viewer axes
const ft = `${dir}/far_trees.bin`;
for (const { within } of areas) if (existsSync(ft)) {
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
