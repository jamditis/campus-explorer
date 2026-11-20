// Pure logic for the landmark hunt (viewer/hunt.js): targets, the found test, the nearest target
// and the pointer angle. No three.js and no DOM, so node --test can run it.
// Positions are viewer metres (+X east, -Z grid north); only x and z matter here.
import { CAMPUS, gridToTrueBearing } from './geo.js';

/** Places from places.json that make up the hunt, in list order. */
export const TARGET_NAMES = Object.freeze([
  'Red Hawk Deck', 'Alexander Kasser Theater', 'Amphitheater', 'Susan A. Cole Hall',
  'College of Communication and Media', 'Memorial Auditorium', 'Sprague Library', 'Student Center',
]);

/** Shorter names for the list and toasts, where the full name is long. */
const SHORT = { 'Alexander Kasser Theater': 'Kasser Theater', 'College of Communication and Media': 'College of Communication' };

/** The bronze Red Hawk statue is not in OpenStreetMap. Position from the model. */
export const STATUE = Object.freeze({ name: 'Red Hawk statue', kind: 'landmark', x: -175, z: 112, r: 2, source: 'model' });

/** Metres beyond a target's radius that still count as reaching it. */
export const REACH = 12;

/** The hunt's targets: the named places that exist in `places`, then the statue. Each gets a `label`. */
export function selectTargets(places) {
  const byName = new Map(places.map(p => [p.name, p]));
  const out = [];
  for (const name of TARGET_NAMES) {
    const p = byName.get(name);
    if (p) out.push({ ...p, label: SHORT[name] || name });
  }
  out.push({ ...STATUE, label: STATUE.name });
  return out;
}

/** Horizontal distance in metres between two points. */
export function horizontalDistance(a, b) {
  return Math.hypot(b.x - a.x, b.z - a.z);
}

/** True when `pos` is within the target's radius plus REACH, horizontally. */
export function isFound(target, pos) {
  return horizontalDistance(target, pos) <= (target.r || 0) + REACH;
}

/** Nearest target whose name is not in `found` (a Set or array): { target, distance } or null. */
export function nearestTarget(targets, found, pos) {
  const has = found instanceof Set ? n => found.has(n) : n => found.includes(n);
  let best = null;
  for (const t of targets) {
    if (has(t.name)) continue;
    const d = horizontalDistance(pos, t);
    if (!best || d < best.distance) best = { target: t, distance: d };
  }
  return best;
}

/**
 * Angle of the pointer toward `target`, relative to the view, in degrees in (-180, 180]:
 * 0 is straight ahead, 90 to the right. `headingTrue` is the view bearing from true north
 * (app.heading()), so the target's grid bearing is converted to true north first.
 */
export function arrowAngle(pos, target, headingTrue) {
  const grid = Math.atan2(target.x - pos.x, -(target.z - pos.z)) * 180 / Math.PI;
  const bearing = gridToTrueBearing(grid, CAMPUS.lat, CAMPUS.lon);
  let rel = (bearing - headingTrue) % 360;
  if (rel <= -180) rel += 360;
  if (rel > 180) rel -= 360;
  return rel;
}

/** Elapsed milliseconds as text, such as `45 s`, `4 min 12 s` or `1 h 3 min`. */
export function formatElapsed(ms) {
  const s = Math.max(0, Math.round(ms / 1000));
  if (s < 60) return `${s} s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} min ${s % 60} s`;
  return `${Math.floor(m / 60)} h ${m % 60} min`;
}

/** Read saved progress: { found: string[], start: number|null, end: number|null }. Bad data gives a fresh state. */
export function parseProgress(text) {
  try {
    const d = JSON.parse(text);
    const found = Array.isArray(d?.found) ? d.found.filter(n => typeof n === 'string') : [];
    const num = v => (typeof v === 'number' && isFinite(v) ? v : null);
    return { found, start: num(d?.start), end: num(d?.end) };
  } catch {
    return { found: [], start: null, end: null };
  }
}
