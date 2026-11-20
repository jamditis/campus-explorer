// Pure geometry for skyline.mjs's step (farcut.mjs): the outline of very distant buildings as seen from the
// campus, and a light stand-in that keeps it. No dependencies, unit-tested from node --test.
// build_web.sh copies this file next to farcut.mjs before it runs it.
// Frame: model metres, x east, y grid north, z up. Angles in degrees.

const DEG = 180 / Math.PI;

/** Bearing of the plan direction (dx, dy): clockwise from grid north, 0 to 360. */
export function bearing(dx, dy) {
  const b = Math.atan2(dx, dy) * DEG;
  return b < 0 ? b + 360 : b;
}

/**
 * The skyline seen from `eye` ([x, y, z]): for each bearing bin of `step` degrees (bin i covers
 * i * step to (i + 1) * step), the highest elevation angle any triangle reaches there (`e`, -Infinity where
 * nothing is) and the point that reaches it (`x`, `y`, `z`, plan distance `r`). Each triangle is cut by
 * the sight ray at every bin centre it spans; its corners count in their own bins too, so a tower
 * narrower than a bin is not lost. `zMin` is the lowest height of any triangle (the curtain's foot).
 * `tris`: 9 numbers per triangle.
 */
export function profile(tris, eye, step) {
  const n = Math.round(360 / step);
  const e = new Float64Array(n).fill(-Infinity), r = new Float64Array(n);
  const x = new Float64Array(n), y = new Float64Array(n), z = new Float64Array(n);
  const [ex, ey, ez] = eye;
  let zMin = Infinity;
  const put = (px, py, pz) => {
    const dx = px - ex, dy = py - ey, d = Math.hypot(dx, dy);
    if (d < 1e-9) return;
    const i = Math.min(n - 1, Math.floor(bearing(dx, dy) / step)), el = Math.atan2(pz - ez, d) * DEG;
    if (el > e[i]) { e[i] = el; r[i] = d; x[i] = px; y[i] = py; z[i] = pz; }
  };
  for (let t = 0; t < tris.length; t += 9) {
    const P = [0, 3, 6].map(o => [tris[t + o], tris[t + o + 1], tris[t + o + 2]]);
    for (const p of P) { put(...p); zMin = Math.min(zMin, p[2]); }
    // bearing span of the triangle, unwrapped across north
    let b = P.map(p => bearing(p[0] - ex, p[1] - ey));
    if (Math.max(...b) - Math.min(...b) > 180) b = b.map(v => (v < 180 ? v + 360 : v));
    const lo = Math.min(...b), hi = Math.max(...b);
    if (hi - lo > 90) continue; // a triangle round the eye: its corners are enough
    for (let k = Math.ceil(lo / step - 0.5); (k + 0.5) * step <= hi; k++) {
      const th = (k + 0.5) * step / DEG, dx = Math.sin(th), dy = Math.cos(th);
      for (let j = 0; j < 3; j++) {
        const p = P[j], q = P[(j + 1) % 3];
        const px = p[0] - ex, py = p[1] - ey, qx = q[0] - ex, qy = q[1] - ey;
        const cp = dx * py - dy * px, cq = dx * qy - dy * qx;
        if ((cp > 0 && cq > 0) || (cp < 0 && cq < 0) || cp === cq) continue;
        const s = cp / (cp - cq), ix = px + s * (qx - px), iy = py + s * (qy - py);
        if (ix * dx + iy * dy <= 0) continue; // behind the eye
        put(ex + ix, ey + iy, p[2] + s * (q[2] - p[2]));
      }
    }
  }
  return { step, e, r, x, y, z, zMin: zMin === Infinity ? 0 : zMin };
}

/** Douglas-Peucker on outline points ({ b, e }, degrees) by distance in the bearing-elevation plane. */
function keep(P, tol) {
  const out = new Set([0, P.length - 1]);
  const stack = [[0, P.length - 1]];
  while (stack.length) {
    const [a, c] = stack.pop();
    const db = P[c].b - P[a].b, de = P[c].e - P[a].e, len = Math.hypot(db, de);
    let worst = -1, far = tol;
    for (let k = a + 1; k < c; k++) {
      const qb = P[k].b - P[a].b, qe = P[k].e - P[a].e;
      const d = len ? Math.abs(db * qe - de * qb) / len : Math.hypot(qb, qe);
      if (d > far) { far = d; worst = k; }
    }
    if (worst > 0) { out.add(worst); stack.push([a, worst], [worst, c]); }
  }
  return [...out].sort((p, q) => p - q).map(k => P[k]);
}

/**
 * The profile as runs of bins with something in them (a run may wrap past 360 degrees: its bearings go on
 * past 360). Each run is a stepped outline, flat over each bin at its height, so a tower one bin wide keeps
 * its vertical sides; then only the points where it turns by more than `tol` degrees are kept.
 * Returns arrays of points { b: bearing, e: elevation, r: plan distance of the bin's highest point }.
 */
export function simplify({ e, r, step }, tol) {
  const n = e.length, full = i => e[i] > -Infinity;
  const gap = [...e.keys()].find(i => !full(i));
  const runs = [];
  let run = [];
  for (let s = 1; s <= n; s++) {
    const i = gap === undefined ? s - 1 : (gap + s) % n;
    if (full(i)) run.push(i);
    else if (run.length) { runs.push(run); run = []; }
  }
  if (run.length) runs.push(run);
  return runs.map(bins => {
    const P = [];
    let turn = 0;
    bins.forEach((i, k) => {
      if (k && i < bins[k - 1]) turn += 360; // past north
      for (const b of [i * step + turn, (i + 1) * step + turn]) {
        const last = P[P.length - 1];
        if (!last || last.b !== b || last.e !== e[i]) P.push({ b, e: e[i], r: r[i] });
      }
    });
    return keep(P, tol);
  });
}

/**
 * The stand-in: a curtain through the outline points, each from its top (at the point's elevation angle and
 * distance) down to the lowest source height, with level normals facing the eye. Two vertices a point (top,
 * then foot) and two triangles between neighbours. Model frame.
 * `reach` (metres, 0 for none): a point farther than that from the eye comes nearer along its sight line,
 * top and foot each keeping their elevation angle, so the outline from the eye stays the same while the
 * whole curtain stays inside the viewer's far plane.
 */
export function curtain(runs, prof, eye, reach = 0) {
  const pos = [], nor = [], index = [];
  for (const run of runs) {
    const first = pos.length / 3;
    run.forEach((p, k) => {
      const th = p.b / DEG, dx = Math.sin(th), dy = Math.cos(th);
      const d = reach > 0 && p.r > reach ? reach : p.r, s = d / p.r;
      const x = eye[0] + dx * d, y = eye[1] + dy * d;
      pos.push(x, y, eye[2] + d * Math.tan(p.e / DEG), x, y, eye[2] + (prof.zMin - eye[2]) * s);
      nor.push(-dx, -dy, 0, -dx, -dy, 0);
      if (k) {
        const a = first + 2 * (k - 1), b = a + 2; // a, a+1: previous top, foot; b, b+1: this top, foot
        index.push(a, a + 1, b, b, a + 1, b + 1);
      }
    });
  }
  return { position: Float32Array.from(pos), normal: Float32Array.from(nor), index: Uint32Array.from(index) };
}

/**
 * True when every corner of the triangles (9 numbers each, model frame) lies farther than `dist` from the
 * origin in plan. Corners, not the bounding box: a mesh of towers joined along an arc has a box that
 * reaches far nearer the campus than any of its parts.
 */
export function beyond(tris, dist) {
  if (!tris.length) return false;
  for (let i = 0; i < tris.length; i += 3) if (Math.hypot(tris[i], tris[i + 1]) <= dist) return false;
  return true;
}
