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
