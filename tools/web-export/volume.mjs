// Pure geometry for supersede.mjs's volumes (an area that owns no ground, such as a building rebuilt by the scripted
// build): take the part of a mesh that lies inside a ring (at any height, or only above a level, below one, or between) out of it, cutting
// every triangle the ring's walls or the level cross exactly there, so a wall or an eave that runs on past the ring
// ends clean on it. No dependencies; unit-tested from node --test. build_web.sh copies it next to supersede.mjs.
import { crossings, cornersIn, edgesCross, outsidePart } from './cut.mjs';

/** A pattern of the plan files: Python's leading `(?i)` (case-insensitive) becomes the `i` flag. */
export function pattern(s) {
  return s.startsWith('(?i)') ? new RegExp(s.slice(4), 'i') : new RegExp(s);
}

/** The ring as cut uses it: moved by a fraction of a millimetre (so no corner of a mesh drawn on a round grid lies
 * exactly on it), its box, and an inside test. */
export function region(ring) {
  const r = ring.map(([x, y]) => [x + 1.37e-4, y + 2.71e-4]);
  const bx = [Math.min(...r.map(p => p[0])), Math.min(...r.map(p => p[1])), Math.max(...r.map(p => p[0])), Math.max(...r.map(p => p[1]))];
  const inside = (x, y) => {
    let hit = false;
    for (let i = 0, j = r.length - 1; i < r.length; j = i++) {
      const a = r[i], b = r[j];
      if ((a[1] > y) !== (b[1] > y) && x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])) hit = !hit;
    }
    return hit;
  };
  return { ring: r, bx, within: (x, y) => x >= bx[0] && x <= bx[2] && y >= bx[1] && y <= bx[3] && inside(x, y) };
}

/**
 * Cut the triangles `tris` (flat list of corner indices) by one volume: `reg` from region(), `above` and `below`
 * levels or null (the volume is the band between them: a door through a wall).
 * `pts` holds the corners' model-frame positions { X, Y, Z } (arrays) and grows by the corners the cut adds; `added`
 * gets, for each added corner, its parents [[corner, weight], ...] (earlier corners, original or added), so every
 * vertex attribute can be interpolated the same way. Returns { keep: flat corner list, removed, cut }.
 * A triangle inside the ring (and between the levels) goes; one that a wall of the ring or a level crosses keeps
 * exactly its part outside the volume. Edges that two triangles share are cut at one shared new corner.
 */
export function cutVolume(pts, added, tris, reg, above = null, below = null) {
  const { X, Y, Z } = pts, { ring, bx, within } = reg;
  const keep = [], memo = new Map(), inn = new Map();
  let removed = 0, cut = 0;
  const isIn = i => { let v = inn.get(i); if (v === undefined) { v = within(X[i], Y[i]) ? 1 : 0; inn.set(i, v); } return v; };
  const add = (key, parents) => {
    let m = key === null ? undefined : memo.get(key);
    if (m === undefined) {
      m = X.length; added.push(parents);
      X.push(parents.reduce((s, [i, k]) => s + X[i] * k, 0));
      Y.push(parents.reduce((s, [i, k]) => s + Y[i] * k, 0));
      Z.push(parents.reduce((s, [i, k]) => s + Z[i] * k, 0));
      if (key !== null) memo.set(key, m);
    }
    return m;
  };
  const pair = (a, b) => (a < b ? `${a},${b}` : `${b},${a}`);
  const P = i => [X[i], Y[i]];
  const mid = (a, b) => add('m' + pair(a, b), [[a, 0.5], [b, 0.5]]);
  const plain = (a, b, c) => [[a, b], [b, c], [c, a]].every(([u, v]) => crossings(X[u], Y[u], X[v], Y[v], ring).length === (isIn(u) !== isIn(v) ? 1 : 0));
  const ringCut = (a, b, c, depth) => {
    const k = isIn(a) + isIn(b) + isIn(c);
    const away = Math.max(X[a], X[b], X[c]) < bx[0] || Math.min(X[a], X[b], X[c]) > bx[2] ||
      Math.max(Y[a], Y[b], Y[c]) < bx[1] || Math.min(Y[a], Y[b], Y[c]) > bx[3];
    if (away) { keep.push(a, b, c); return; }
    const tri = [P(a), P(b), P(c)], corners = cornersIn(ring, ...tri);
    // a wall seen from above is a line: all its corners can lie inside while the ring leaves and comes back
    const crossed = !corners.length && (k === 0 || k === 3) && edgesCross(ring, tri);
    if (!corners.length && k === 3 && !crossed) { removed++; return; }
    if (!corners.length && k === 0 && !crossed) { keep.push(a, b, c); return; }
    const simple = k > 0 && k < 3 && corners.length <= 1 && plain(a, b, c);
    const longest = Math.max(Math.hypot(X[a] - X[b], Y[a] - Y[b], Z[a] - Z[b]), Math.hypot(X[b] - X[c], Y[b] - Y[c], Z[b] - Z[c]),
      Math.hypot(X[c] - X[a], Y[c] - Y[a], Z[c] - Z[a]));
    if (depth < 16 && longest > 0.05 && !simple) {
      const ab = mid(a, b), bc = mid(b, c), ca = mid(c, a);
      ringCut(a, ab, ca, depth + 1); ringCut(ab, b, bc, depth + 1); ringCut(ca, bc, c, depth + 1); ringCut(ab, bc, ca, depth + 1);
      return;
    }
    if (!simple) { if (k >= 2) removed++; else keep.push(a, b, c); return; } // a few centimetres across by now
    const ids = [a, b, c];
    const at = corners.length ? { index: corners[0], at: ring[corners[0]] } : null;
    const part = outsidePart(ring, tri, ids.map(i => isIn(i) === 1), at, 0);
    const vs = part.map(q => {
      if (q.kind === 'corner') return ids[q.i];
      if (q.kind === 'cross') { const i = ids[q.edge[0]], o = ids[q.edge[1]]; return add(`x${i},${o}`, [[i, 1 - q.t], [o, q.t]]); }
      const [[x1, y1], [x2, y2], [x3, y3]] = tri, d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3);
      const l1 = ((y2 - y3) * (q.x - x3) + (x3 - x2) * (q.y - y3)) / d, l2 = ((y3 - y1) * (q.x - x3) + (x1 - x3) * (q.y - y3)) / d;
      return add(null, [[a, l1], [b, l2], [c, 1 - l1 - l2]]);
    });
    const s0 = Math.max(0, part.findIndex(q => q.kind === 'ring'));
    for (let j = 1; j < vs.length - 1; j++) keep.push(vs[s0], vs[(s0 + j) % vs.length], vs[(s0 + j + 1) % vs.length]);
    cut++;
  };
  // split a corner list (a convex polygon) at a level: [the part above, the part at or below]
  const split = (ids, level) => {
    const up = ids.map(i => Z[i] > level), hi = [], lo = [];
    for (let e = 0; e < ids.length; e++) {
      const u = ids[e], v = ids[(e + 1) % ids.length];
      (up[e] ? hi : lo).push(u);
      if (up[e] !== up[(e + 1) % ids.length]) {
        const [i, j] = u < v ? [u, v] : [v, u], s = (level - Z[i]) / (Z[j] - Z[i]);
        const m = add(`p${level}:` + pair(i, j), [[i, 1 - s], [j, s]]);
        hi.push(m); lo.push(m);
      }
    }
    return [hi, lo];
  };
  const fan = (poly, f) => { for (let j = 1; j < poly.length - 1; j++) f(poly[0], poly[j], poly[j + 1]); };
  const stay = (a, b, c) => keep.push(a, b, c);
  const inRing = (a, b, c) => ringCut(a, b, c, 0);
  for (let t = 0; t < tris.length; t += 3) {
    const a = tris[t], b = tris[t + 1], c = tris[t + 2];
    if (above === null && below === null) { ringCut(a, b, c, 0); continue; }
    const before = keep.length, done = removed + cut;
    // what lies above `below` stays; of the rest, what lies at or below `above` stays; the band between is cut
    let band = [[a, b, c]];
    if (below !== null) {
      const [hi, lo] = split([a, b, c], below);
      fan(hi, stay); band = lo.length >= 3 ? [lo] : [];
    }
    for (const poly of band) {
      if (above === null) { fan(poly, inRing); continue; }
      const [hi, lo] = split(poly, above);
      fan(lo, stay); fan(hi, inRing);
    }
    // nothing went after all: the triangle stays whole (its split corners go unused)
    if (removed + cut === done) { keep.length = before; keep.push(a, b, c); }
  }
  return { keep, removed, cut };
}
