// Pure maths for the measuring tool (viewer/measure.js): path totals, slope, bearing and text.
// No three.js and no DOM, so node --test can run it. Points are viewer metres { x, y, z }
// (+X east, +Y up, -Z grid north).
import { localToLatLon, gridToTrueBearing, compassPoint, formatDistance } from './geo.js';

/** A press counts as a click when it moves less than this many pixels... */
export const CLICK_PX = 5;
/** ...and is released within this many milliseconds. Anything else is a drag that orbits. */
export const CLICK_MS = 400;

/** True when a pointer press and release ({ x, y, t } in px and ms) form a click, not a drag. */
export function isClick(down, up) {
  return Math.hypot(up.x - down.x, up.y - down.y) < CLICK_PX && up.t - down.t < CLICK_MS;
}

/** Grid bearing from a to b in degrees clockwise from grid north, in [0, 360). */
export function gridBearing(a, b) {
  const deg = Math.atan2(b.x - a.x, -(b.z - a.z)) * 180 / Math.PI;
  return (deg + 360) % 360;
}

/** True bearing from a to b in degrees clockwise from true north, using the convergence at a. */
export function trueBearing(a, b) {
  const { lat, lon } = localToLatLon(a.x, a.z);
  return gridToTrueBearing(gridBearing(a, b), lat, lon);
}

/**
 * Totals for a path of points.
 * Returns { count, segments, path, straight, horizontal, rise, slope, bearing }:
 * segment lengths and path length (3D), straight-line distance first to last (3D), horizontal run
 * first to last, rise (last minus first, signed), and for exactly two points the slope in percent
 * (null when the run is too short to mean anything) and the true bearing in degrees (null when the
 * points are vertically aligned). With fewer than two points the distances are 0.
 */
export function pathTotals(points) {
  const count = points.length;
  const segments = [];
  for (let i = 1; i < count; i++) segments.push(dist3(points[i - 1], points[i]));
  const path = segments.reduce((s, d) => s + d, 0);
  if (count < 2) return { count, segments, path, straight: 0, horizontal: 0, rise: 0, slope: null, bearing: null };
  const a = points[0], b = points[count - 1];
  const horizontal = Math.hypot(b.x - a.x, b.z - a.z);
  const rise = b.y - a.y;
  const two = count === 2;
  return {
    count, segments, path,
    straight: dist3(a, b),
    horizontal, rise,
    slope: two && horizontal >= 0.01 ? rise / horizontal * 100 : null,
    bearing: two && horizontal >= 0.01 ? trueBearing(a, b) : null,
  };
}

function dist3(a, b) {
  return Math.hypot(b.x - a.x, b.y - a.y, b.z - a.z);
}

/** Signed height difference as text, such as `+2.4 m · +7.9 ft` or `−0.6 m · −2.0 ft`. */
export function formatRise(m) {
  if (Math.abs(m) < 0.05) return formatDistance(0);
  const sign = m > 0 ? '+' : '−';
  return formatDistance(Math.abs(m)).replace(/(^|· )/g, `$1${sign}`);
}

/** Slope in percent as signed text, such as `+4.2 %` (uphill from the first point) or `−12 %`. */
export function formatSlope(pct) {
  if (pct === null || !isFinite(pct)) return '';
  const a = Math.abs(pct);
  if (a < 0.05) return '0.0 %';
  const sign = pct > 0 ? '+' : '−';
  return `${sign}${a >= 100 ? Math.round(a) : a.toFixed(1)} %`;
}

/** True bearing as text, such as `123° ESE`. */
export function formatBearing(deg) {
  if (deg === null || !isFinite(deg)) return '';
  return `${Math.round(deg) % 360}° ${compassPoint(deg)}`;
}
