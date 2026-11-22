// Pure geometry for supersede.mjs: cut a small triangle of another source's ground exactly at a footprint
// outline, so that ground ends at the outline at its own height. No dependencies, unit-tested from node --test.
// build_web.sh copies this file next to supersede.mjs before it runs it.

/** Where the segment (ax, ay)-(bx, by) crosses the closed outline `ring`: the parameters t in (0, 1), sorted. */
export function crossings(ax, ay, bx, by, ring) {
  const out = [], dx = bx - ax, dy = by - ay;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [px, py] = ring[j], [qx, qy] = ring[i], ex = qx - px, ey = qy - py;
    const den = dx * ey - dy * ex;
    if (Math.abs(den) < 1e-15) continue; // parallel
    const t = ((px - ax) * ey - (py - ay) * ex) / den, u = ((px - ax) * dy - (py - ay) * dx) / den;
    if (t > 0 && t < 1 && u >= 0 && u < 1) out.push(t);
  }
  return out.sort((a, b) => a - b);
}

/** Indices of the outline's corners that lie inside the triangle a, b, c (either winding). */
export function cornersIn(ring, a, b, c) {
  const side = (p, q, r) => (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);
  const s = Math.sign(side(a, b, c)), out = [];
  if (!s) return out;
  const lo = [Math.min(a[0], b[0], c[0]), Math.min(a[1], b[1], c[1])];
  const hi = [Math.max(a[0], b[0], c[0]), Math.max(a[1], b[1], c[1])];
  ring.forEach((p, i) => {
    if (p[0] < lo[0] || p[0] > hi[0] || p[1] < lo[1] || p[1] > hi[1]) return;
    if (side(a, b, p) * s > 0 && side(b, c, p) * s > 0 && side(c, a, p) * s > 0) out.push(i);
  });
  return out;
}

/** Whether the outline crosses any edge of the triangle a, b, c (a band of footprint can cross a triangle with no
 * corner of either inside the other). */
export function edgesCross(ring, [a, b, c]) {
  return [[a, b], [b, c], [c, a]].some(([p, q]) => crossings(p[0], p[1], q[0], q[1], ring).length > 0);
}

/**
 * The part of triangle `tri` ([[x, y] x3]) that lies outside the footprint `ring`, as a polygon in the triangle's own
 * winding, for a small triangle the outline crosses once: `isIn` says which corners are inside; `corner`
 * ({ index, at }) is the one outline corner inside the triangle, or null.
 * Items: { kind: 'corner', i } a corner of the triangle that stays; { kind: 'cross', edge: [inside, outside], t }
 * the point on that edge where the outline crosses it, t measured from the inside corner (the same for both
 * triangles that share the edge); { kind: 'ring', index } the outline corner. Every item has its x, y.
 * `over` pulls each crossing that many metres back along its edge toward the inside corner, so the cut ground
 * reaches a little under the new ground and rounding its position cannot open a crack.
 */
export function outsidePart(ring, tri, isIn, corner, over = 0) {
  const out = [];
  for (let k = 0; k < 3; k++) {
    const u = k, v = (k + 1) % 3;
    if (!isIn[u]) out.push({ kind: 'corner', i: u, x: tri[u][0], y: tri[u][1] });
    if (isIn[u] !== isIn[v]) {
      const [i, o] = isIn[u] ? [u, v] : [v, u];
      const [ix, iy] = tri[i], [ox, oy] = tri[o];
      const ts = crossings(ix, iy, ox, oy, ring);
      // the crossing nearest the outside corner bounds the ground that stays
      let t = ts.length ? ts[ts.length - 1] : 0.5;
      const len = Math.hypot(ox - ix, oy - iy) || 1;
      t = Math.max(0, t - over / len);
      out.push({ kind: 'cross', edge: [i, o], t, x: ix + (ox - ix) * t, y: iy + (oy - iy) * t });
      // the outline turns at its corner between leaving the triangle's inside and coming back out
      if (corner && isIn[v]) out.push({ kind: 'ring', index: corner.index, x: corner.at[0], y: corner.at[1] });
    }
  }
  return out;
}

/** Distance from (x, y) to the closed outline `ring`. */
export function ringDistance(ring, x, y) {
  let best = Infinity;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [ax, ay] = ring[j], dx = ring[i][0] - ax, dy = ring[i][1] - ay;
    const t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / ((dx * dx + dy * dy) || 1e-12)));
    best = Math.min(best, Math.hypot(x - ax - t * dx, y - ay - t * dy));
  }
  return best;
}

const COARSE = 0.1; // metres between grid points: the north model's far field (0.38 m), not the skirt (6 cm)

/**
 * Where a vertex the outline cut is stored in a quantised mesh (KHR_mesh_quantization: normalized integers, `div`
 * steps per node unit). Rounded to the nearest grid point, a vertex moves up to half a step either way, and the far
 * field's grid is coarse (0.38 m in the north model's 12 km BD_farfield_3DEP, 6 cm in the 4 km skirt): its cut edge
 * ended up to a quarter metre short of the outline, a crack that showed the ground below. Instead, of the grid
 * points round the exact point `q` (node units), the one nearest it in the model frame (`toModel` maps node units
 * to [x, y, z] metres) that `keep(x, y)` accepts (inside the outline, under the new ground), as integers. Up (the node
 * axis that is most of model z) is rounded to the nearest. Where the point has to move off plain rounding and `level`
 * is given (node units in, the up coordinate of the ground's own surface there out), up is that surface's height at
 * the new point, rounded, and on a grid of COARSE or more, of the accepted points up to a grid step further than the
 * nearest the one whose rounded height lies nearest that surface: on the far field's slopes (0.4 m a metre) and its 0.38 m height steps a moved
 * corner would otherwise stand up to 0.4 m off the ground it was cut from. A face steeper than 45 degrees (a skirt's
 * drop) keeps the rounded height. The nearest grid point when none of them is accepted.
 */
export function snapQuantized(q, div, toModel, keep, reach = 3, level = null) {
  // the same corner reached from two triangles can differ in the last bits: the same input, the same grid point
  q = q.map(v => Math.round(v * 1e9) / 1e9);
  const o = toModel([0, 0, 0]), signed = div === 127 || div === 32767;
  const rise = [0, 1, 2].map(a => { const e = [0, 0, 0]; e[a] = 1; return Math.abs(toModel(e)[2] - o[2]); });
  const up = rise.indexOf(Math.max(...rise)), [h0, h1] = [0, 1, 2].filter(a => a !== up);
  const clamp = v => Math.max(signed ? -div : 0, Math.min(div, v));
  const plain = q.map(v => clamp(Math.round(v * div)));
  const at = toModel(q), base = q.map(v => Math.floor(v * div)), cands = [];
  for (let i = 1 - reach; i <= reach; i++) for (let j = 1 - reach; j <= reach; j++) {
    const c = base.slice();
    c[h0] = clamp(c[h0] + i); c[h1] = clamp(c[h1] + j); c[up] = plain[up];
    const m = toModel(c.map(v => v / div));
    cands.push([Math.hypot(m[0] - at[0], m[1] - at[1], m[2] - at[2]), c, m]);
  }
  cands.sort((a, b) => a[0] - b[0]);
  const ok = cands.filter(([, , m]) => keep(m[0], m[1]));
  if (!ok.length) return plain;
  const [d0, c0] = ok[0];
  if (!level || (c0[h0] === plain[h0] && c0[h1] === plain[h1])) return c0;
  // moved off plain rounding: of the accepted points up to a step further, the one whose rounded height lies nearest
  // the ground's own surface there, on a face no steeper than 45 degrees (a skirt's drop: the plane would throw the
  // corner up or down, so it keeps the rounded height)
  const e0 = [0, 0, 0]; e0[h0] = 1 / div;
  const g = toModel(e0), step = Math.hypot(g[0] - o[0], g[1] - o[1]); // metres between grid points
  let best = c0, err = Infinity;
  for (const [d, c, m] of ok) {
    // a further point only on a grid as coarse as the north model's far field (on a finer one its height error is
    // small, and two corners on an edge that moved apart leave a pinhole)
    if (d > d0 + (step >= COARSE ? step : 0) + 1e-9) break;
    const v = c.slice(); v[up] = level(c.map(u => u / div)) * div;
    const t = toModel(v.map(u => u / div));
    if (Math.abs(t[2] - at[2]) > Math.hypot(m[0] - at[0], m[1] - at[1])) continue;
    const e = Math.abs(Math.round(v[up]) - v[up]);
    if (e < err - 1e-9) { err = e; best = c.slice(); best[up] = clamp(Math.round(v[up])); }
  }
  return best;
}

/** The up coordinate (axis `up`) of the plane through three points (node units) at the horizontal place of `p`. */
export function planeLevel(p0, p1, p2, up) {
  const [h0, h1] = [0, 1, 2].filter(a => a !== up);
  const d = (p1[h1] - p2[h1]) * (p0[h0] - p2[h0]) + (p2[h0] - p1[h0]) * (p0[h1] - p2[h1]);
  return p => {
    if (!d) return p[up];
    const l0 = ((p1[h1] - p2[h1]) * (p[h0] - p2[h0]) + (p2[h0] - p1[h0]) * (p[h1] - p2[h1])) / d;
    const l1 = ((p2[h1] - p0[h1]) * (p[h0] - p2[h0]) + (p0[h0] - p2[h0]) * (p[h1] - p2[h1])) / d;
    return l0 * p0[up] + l1 * p1[up] + (1 - l0 - l1) * p2[up];
  };
}

/**
 * How far (x, y) lies behind the outline's corner `i`: the smaller of its distances inside the lines of the two runs
 * that meet there (negative in front of either). A far-field corner stored at an outline corner must lie behind both:
 * at a reflex corner a point can be inside the outline but in front of one run, and the far field's edge from it then
 * crosses the outline and leaves a sliver of the wedge beyond it bare.
 */
export function behind(ring, i, x, y) {
  let s = 0;
  for (let k = 0, j = ring.length - 1; k < ring.length; j = k++) s += ring[j][0] * ring[k][1] - ring[k][0] * ring[j][1];
  const o = Math.sign(s) || 1, n = ring.length, c = ring[i];
  const side = (a, b) => { // inside of the run a -> b is to its left when the outline runs anticlockwise
    const dx = b[0] - a[0], dy = b[1] - a[1], ln = Math.hypot(dx, dy) || 1;
    return o * (dx * (y - a[1]) - dy * (x - a[0])) / ln;
  };
  return Math.min(side(ring[(i + n - 1) % n], c), side(c, ring[(i + 1) % n]));
}

/**
 * The triangles `keep` (corner indices, three a triangle) split into those that hold a corner the outline cut (an
 * added corner, index n + k with k in `onLine`) and the rest: the cut pieces of a coarsely quantised far field go to a
 * primitive with exact positions, the rest keeps its grid.
 */
export function splitEdge(keep, n, onLine) {
  const rest = [], edge = [];
  for (let t = 0; t < keep.length; t += 3) {
    const tri = [keep[t], keep[t + 1], keep[t + 2]];
    (tri.some(v => v >= n && onLine.has(v - n)) ? edge : rest).push(...tri);
  }
  return { rest, edge };
}
