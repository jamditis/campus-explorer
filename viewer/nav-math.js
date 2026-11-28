// Pure maths for viewer/nav.js: progress along a route, its turns, and the direction arrow.
// Points are [x, z] in viewer metres (+x east, -z grid north). No imports.

const DEG = 180 / Math.PI;
const MERGE_M = 6;     // bends closer together than this count as one turn
const TURN_DEG = 30;   // a smaller change of direction is not a turn

/** Grid bearing of the step from a to b, degrees clockwise from -z. */
export function bearing(ax, az, bx, bz) {
  const d = Math.atan2(bx - ax, -(bz - az)) * DEG;
  return d < 0 ? d + 360 : d;
}
const turnOf = (b0, b1) => { const d = ((b1 - b0) % 360 + 540) % 360 - 180; return d; }; // + is a right turn

/** { pts, at: cumulative metres at each point, length } */
export function polyline(points) {
  const at = [0];
  for (let i = 1; i < points.length; i++) at.push(at[i - 1] + Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]));
  return { pts: points, at, length: at[at.length - 1] ?? 0 };
}

/**
 * Where (x, z) is along the line: { s (metres from the start), off (metres from the line), seg }.
 * Segments from `from` - 1 on are searched, so a route that doubles back does not jump ahead or back.
 */
export function progress(line, x, z, from = 0) {
  let best = { s: 0, off: Infinity, seg: 0 };
  for (let i = Math.max(0, from - 1); i < line.pts.length - 1; i++) {
    const [ax, az] = line.pts[i], [bx, bz] = line.pts[i + 1];
    const dx = bx - ax, dz = bz - az, len2 = dx * dx + dz * dz;
    const t = len2 > 0 ? Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / len2)) : 0;
    const off = Math.hypot(x - ax - t * dx, z - az - t * dz);
    if (off < best.off - 1e-9) best = { s: line.at[i] + t * Math.sqrt(len2), off, seg: i };
  }
  return best;
}

/** The point `s` metres along the line, clamped to its ends. */
export function pointAt(line, s) {
  const { pts, at } = line;
  if (s <= 0 || pts.length < 2) return pts[0];
  for (let i = 1; i < pts.length; i++) {
    if (at[i] >= s) {
      const t = (s - at[i - 1]) / ((at[i] - at[i - 1]) || 1);
      return [pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t];
    }
  }
  return pts[pts.length - 1];
}

/**
 * The turns along the line: [{ s, angle }] where angle is the change of direction in degrees (+ right).
 * Bends within MERGE_M of each other add up into one turn at their middle; under TURN_DEG is no turn.
 */
export function turns(line) {
  const { pts, at } = line, out = [];
  const bends = [];
  for (let i = 1; i < pts.length - 1; i++) {
    const b0 = bearing(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1]);
    const b1 = bearing(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]);
    bends.push({ s: at[i], angle: turnOf(b0, b1) });
  }
  for (let i = 0; i < bends.length;) {
    let j = i, sum = bends[i].angle;
    while (j + 1 < bends.length && bends[j + 1].s - bends[j].s < MERGE_M) sum += bends[++j].angle;
    if (Math.abs(sum) >= TURN_DEG) out.push({ s: (bends[i].s + bends[j].s) / 2, angle: sum });
    i = j + 1;
  }
  return out;
}

/** Words for a turn angle: 'Slight right', 'Turn left', 'Sharp right' and so on. */
export function turnWords(angle) {
  const side = angle > 0 ? 'right' : 'left', a = Math.abs(angle);
  return a < 50 ? `Slight ${side}` : a < 130 ? `Turn ${side}` : `Sharp ${side}`;
}

/**
 * The next thing to tell the walker at `s` metres along: { text, inM, angle } for the next turn,
 * or the arrival when no turn is left. `goal` is the place name.
 */
export function nextStep(line, list, s, goal) {
  const t = list.find(x => x.s > s + 1);
  if (t) return { text: turnWords(t.angle), inM: t.s - s, angle: t.angle };
  return { text: `Arrive at ${goal}`, inM: Math.max(0, line.length - s), angle: 0 };
}

/** Rounded distance for the HUD: 5 m steps under 100 m, 10 m steps under 1 km, then km. */
export function roundDistance(m) {
  if (m < 100) return `${Math.max(5, Math.round(m / 5) * 5)} m`;
  if (m < 1000) return `${Math.round(m / 10) * 10} m`;
  return `${(m / 1000).toFixed(1)} km`;
}

/** Angle in degrees to turn the HUD arrow: the target's bearing from the walker against the view's bearing (+ clockwise). */
export function arrowAngle(x, z, tx, tz, viewBearing) {
  return turnOf(viewBearing, bearing(x, z, tx, tz));
}
