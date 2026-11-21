// Pure maths for the teaser: camera paths (Catmull-Rom splines walked at an eased speed along their
// length), easing curves, the frame-to-shot clock, and the placement and timing of the 3D graphics.
// No three.js and no DOM, so `node --test` covers it (tests/teaser.test.mjs).

const lerp = (a, b, t) => a + (b - a) * t;
export const clamp01 = t => Math.min(1, Math.max(0, t));
const sub = (a, b) => a.map((v, i) => v - b[i]);
const len = a => Math.hypot(...a);

/** Ease curves on [0, 1]. Each starts at 0, ends at 1, and is flat at both ends unless named `out`. */
export const ease = {
  linear: t => clamp01(t),
  smooth: t => { t = clamp01(t); return t * t * (3 - 2 * t); },
  smoother: t => { t = clamp01(t); return t * t * t * (t * (t * 6 - 15) + 10); },
  sine: t => 0.5 - 0.5 * Math.cos(Math.PI * clamp01(t)),
  out: t => 1 - (1 - clamp01(t)) ** 3,
  in: t => clamp01(t) ** 3,
  /** Ease out past 1 and back (a gentle overshoot): for graphics that land. */
  back: t => { t = clamp01(t); const s = 1.4; return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2; },
};

/**
 * Speed profile for a move: accelerate over the first `a` of the shot, cruise, decelerate over the last
 * `b`. Returns the fraction of distance covered at time t (0..1). The speed is continuous (no linear
 * ramp corners): the ends are half-cosine ramps. a = b = 0.5 is a plain sine ease; a = 0 starts at speed.
 */
export function cruise(t, a = 0.3, b = 0.3) {
  t = clamp01(t);
  // speed v(t): ramps 0 -> 1 over [0, a] and 1 -> 0 over [1 - b, 1], 1 between; integrate and normalise
  const ramp = (x, w) => (w > 0 ? (x - (w / Math.PI) * Math.sin((Math.PI * x) / w)) / 2 : x); // ∫ of (1-cos)/2
  const total = (1 - a - b) + a / 2 + b / 2;
  let d;
  if (t < a) d = ramp(t, a);
  else if (t <= 1 - b) d = a / 2 + (t - a);
  else { const r = 1 - t; d = total - ramp(r, b); }
  return d / total;
}

/** Centripetal Catmull-Rom point between p1 and p2 (0 <= t <= 1), with neighbours p0 and p3. */
export function catmull(p0, p1, p2, p3, t) {
  const k = (a, b) => Math.max(1e-6, Math.sqrt(len(sub(b, a))));
  const t0 = 0, t1 = t0 + k(p0, p1), t2 = t1 + k(p1, p2), t3 = t2 + k(p2, p3);
  const u = lerp(t1, t2, t);
  return p1.map((_, i) => {
    const a1 = ((t1 - u) * p0[i] + (u - t0) * p1[i]) / (t1 - t0);
    const a2 = ((t2 - u) * p1[i] + (u - t1) * p2[i]) / (t2 - t1);
    const a3 = ((t3 - u) * p2[i] + (u - t2) * p3[i]) / (t3 - t2);
    const b1 = ((t2 - u) * a1 + (u - t0) * a2) / (t2 - t0);
    const b2 = ((t3 - u) * a2 + (u - t1) * a3) / (t3 - t1);
    return ((t2 - u) * b1 + (u - t1) * b2) / (t2 - t1);
  });
}

/**
 * A spline through `points` (arrays of equal length). The end points get mirrored neighbours, so the
 * curve leaves the first point heading for the second. `at(s)` takes s in [0, 1] as a fraction of the
 * curve's LENGTH, so an eased s gives an eased speed whatever the spacing of the points.
 */
export function spline(points, samples = 64) {
  if (points.length === 1) return { length: 0, at: () => [...points[0]] };
  const n = points.length;
  const P = i => (i < 0 ? points[0].map((v, k) => 2 * v - points[1][k])
    : i >= n ? points[n - 1].map((v, k) => 2 * v - points[n - 2][k]) : points[i]);
  const raw = u => { // u in [0, n - 1]
    const i = Math.min(n - 2, Math.floor(u));
    return catmull(P(i - 1), P(i), P(i + 1), P(i + 2), u - i);
  };
  const m = samples * (n - 1), table = [0];
  let prev = raw(0);
  for (let j = 1; j <= m; j++) { const q = raw((j / m) * (n - 1)); table.push(table[j - 1] + len(sub(q, prev))); prev = q; }
  const total = table[m];
  return {
    length: total,
    at(s) {
      const want = clamp01(s) * total;
      let lo = 0, hi = m;
      while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (table[mid] < want) lo = mid; else hi = mid; }
      const f = table[hi] > table[lo] ? (want - table[lo]) / (table[hi] - table[lo]) : 0;
      return raw(((lo + f) / m) * (n - 1));
    },
  };
}

/** Shot list to a clock: start frame of each shot and the total. Durations in seconds. */
export function timeline(shots, fps) {
  let f = 0;
  const starts = shots.map(s => { const at = f; f += Math.round(s.duration * fps); return at; });
  return { starts, frames: f };
}

/** Which shot a frame belongs to, and its local time: { shot, t (0..1), sec (seconds into the shot) }. */
export function frameAt(frame, shots, fps) {
  const { starts, frames } = timeline(shots, fps);
  if (frame < 0 || frame >= frames) return null;
  let i = starts.length - 1;
  while (starts[i] > frame) i--;
  const n = Math.round(shots[i].duration * fps);
  return { shot: i, t: n > 1 ? (frame - starts[i]) / (n - 1) : 0, sec: (frame - starts[i]) / fps };
}

/**
 * The camera of a shot at local time t: position and look-at point on their splines, walked with the
 * shot's speed profile; fov eased between `fov` and `fov2`; a small "handheld" drift if `drift` (metres)
 * is set, made of slow incommensurate sines so it never repeats or jerks.
 */
export function cameraAt(shot, t) {
  // a shot that is one part of a longer move (`move`, with `span` [from, to] of the move's time):
  // the cut falls mid-move and the speed carries across it
  if (shot.move) return cameraAt(shot.move, lerp(shot.span[0], shot.span[1], clamp01(t)));
  const s = cruise(t, shot.accel ?? 0.3, shot.decel ?? 0.3);
  const pos = spline(shot.pos).at(s), look = spline(shot.look).at(s);
  const fov = lerp(shot.fov ?? 50, shot.fov2 ?? shot.fov ?? 50, ease.sine(t));
  if (shot.drift) {
    const sec = t * shot.duration, d = shot.drift;
    pos[0] += d * (Math.sin(sec * 0.71) * 0.6 + Math.sin(sec * 1.37 + 1) * 0.4);
    pos[1] += d * 0.6 * (Math.sin(sec * 0.93 + 2) * 0.7 + Math.sin(sec * 1.81) * 0.3);
    look[0] += d * 0.8 * Math.sin(sec * 0.57 + 0.5);
    look[1] += d * 0.5 * Math.sin(sec * 0.83 + 3);
  }
  return { pos, look, fov };
}

/** Linear blend of sun times (ISO strings) by an eased t; returns a Date. */
export function timeAt(shot, t) {
  const a = Date.parse(shot.time), b = Date.parse(shot.time2 ?? shot.time);
  return new Date(lerp(a, b, ease.sine(clamp01((t - (shot.timeFrom ?? 0)) / ((shot.timeTo ?? 1) - (shot.timeFrom ?? 0))))));
}

/**
 * How far a graphic is "on" at a time: 0 before `in`, eased up over `inDur`, 1, eased down over `outDur`
 * ending at `out`. Times in seconds of the shot. Returns { on (0..1, eased), raw (0..1, linear) }.
 */
export function presence(g, sec) {
  const inDur = g.inDur ?? 0.6, outDur = g.outDur ?? 0.4, end = g.out ?? Infinity;
  const up = clamp01((sec - (g.in ?? 0)) / inDur), down = clamp01((end - sec) / outDur);
  const raw = Math.min(up, down);
  return { on: up < 1 ? ease.back(up) * (down < 1 ? ease.smooth(down) : 1) : ease.smooth(down), raw, up, down };
}

/**
 * A dimension line from a to b ([x, y, z]), drawn flat in the plane that holds the line and `up`
 * ([0, 1, 0] by default: the line's own vertical plane; pass a normal for a line laid on the ground).
 * Returns { length, mid, dir, side } and the parts as segments: the shaft between the arrowheads,
 * two arrowheads (triangles), two end ticks. `head` is the arrowhead length in metres.
 */
export function dimension(a, b, { head = 2, tick = 2, up = [0, 1, 0] } = {}) {
  const d = sub(b, a), L = len(d), dir = d.map(v => v / L);
  // side: in the plane of dir and up, perpendicular to dir
  const dot = dir.reduce((s, v, i) => s + v * up[i], 0);
  let side = up.map((v, i) => v - dot * dir[i]);
  const sl = len(side); side = sl > 1e-9 ? side.map(v => v / sl) : [0, 1, 0];
  const at = (p, k, s = 0) => p.map((v, i) => v + dir[i] * k + side[i] * s);
  const w = head * 0.38;
  return {
    length: L, dir, side, mid: a.map((v, i) => (v + b[i]) / 2),
    shaft: [at(a, head), at(b, -head)],
    heads: [[a, at(a, head, w), at(a, head, -w)], [b, at(b, -head, w), at(b, -head, -w)]],
    ticks: [[at(a, 0, -tick), at(a, 0, tick)], [at(b, 0, -tick), at(b, 0, tick)]],
  };
}

/** Part of a dimension line drawn at wipe w (0..1): the shaft grows from the middle outwards. */
export function wipeShaft(shaft, w) {
  const [p, q] = shaft, m = p.map((v, i) => (v + q[i]) / 2), k = clamp01(w);
  return [m.map((v, i) => lerp(v, p[i], k)), m.map((v, i) => lerp(v, q[i], k))];
}

/** Yaw (radians about +y) that turns a text's +z face toward point `to` from `at`. */
export function faceYaw(at, to) { return Math.atan2(to[0] - at[0], to[2] - at[2]); }

/** Width of a string in em with plain advances (glyphs: { ch: { adv } }); unknown characters count 0.5. */
export function textWidth(str, glyphs, tracking = 0) {
  let w = 0;
  for (const ch of str) w += (glyphs[ch]?.adv ?? 0.5) + tracking;
  return str.length ? w - tracking : 0;
}

/** The pen x of each character of a string, centred (`align` 'centre') or from 0 ('left'). */
export function layout(str, glyphs, { tracking = 0, align = 'centre' } = {}) {
  const w = textWidth(str, glyphs, tracking);
  let x = align === 'centre' ? -w / 2 : 0;
  const out = [];
  for (const ch of str) { out.push({ ch, x }); x += (glyphs[ch]?.adv ?? 0.5) + tracking; }
  return { width: w, chars: out };
}

/** Letter-by-letter stagger: the local raw time of letter i of n when the whole word is at u (0..1). */
export function stagger(u, i, n, spread = 0.5) {
  if (n <= 1) return clamp01(u);
  const start = (i / (n - 1)) * spread;
  return clamp01((u - start) / (1 - spread));
}
