// Pure. The soft flight limit: the camera may go anywhere over the campus and well beyond it, and is
// eased to a stop at a box around it, so it cannot reach the far stand-ins (city skyline silhouettes),
// which only read right from the campus. No DOM and no three: points are plain { x, y, z }, viewer metres.

/** Metres the limit lies beyond the campus tiles, sideways. */
export const MARGIN = 1000;
/** The limit stays this far inside the far-field skirt, whose edge would otherwise come into view. */
export const SKIRT_INSET = 150;
/** Width of the band inside the limit in which outward motion slows to a stop. */
export const SOFT = 250;
/** The ceiling over the campus floor, in campus spans: above the top view (1.05 spans). */
export const CEILING_SPAN = 1.25;
const TILE = 160; // tile size of models/main (tools/web-export)

/**
 * The limit for the tiles of a manifest: { x0, x1, z0, z1, y1 }, or null when no tile has a centre.
 * The campus tile box grown by MARGIN, cut back to SKIRT_INSET inside the skirt (`skirtHalf`, metres
 * from the origin: the manifest's landcover `half`), and a ceiling CEILING_SPAN spans over `floorY`.
 */
export function flightLimit(tiles, { skirtHalf = 2000, floorY = 100 } = {}) {
  const c = (tiles || []).filter(t => Array.isArray(t.center)).map(t => t.center);
  if (!c.length) return null;
  const h = TILE / 2, edge = skirtHalf - SKIRT_INSET;
  const x0 = Math.min(...c.map(p => p[0])) - h, x1 = Math.max(...c.map(p => p[0])) + h;
  const z0 = Math.min(...c.map(p => p[1])) - h, z1 = Math.max(...c.map(p => p[1])) + h;
  const span = Math.max(x1 - x0, z1 - z0);
  return {
    x0: Math.max(-edge, x0 - MARGIN), x1: Math.min(edge, x1 + MARGIN),
    z0: Math.max(-edge, z0 - MARGIN), z1: Math.min(edge, z1 + MARGIN),
    y1: floorY + span * CEILING_SPAN,
  };
}

// outward speed left at a distance `d` inside a bound: none at the bound, all of it from SOFT in
const ease = d => Math.min(1, Math.max(0, d / SOFT));

/**
 * Velocity `v` at `p` with its outward part slowed over the last SOFT metres before the limit. Only the
 * part across a bound is slowed, so the camera slides along the limit; motion back in is never slowed.
 */
export function limitVelocity(p, v, L) {
  if (!L) return { ...v };
  const out = { ...v };
  if (out.x > 0) out.x *= ease(L.x1 - p.x); else if (out.x < 0) out.x *= ease(p.x - L.x0);
  if (out.z > 0) out.z *= ease(L.z1 - p.z); else if (out.z < 0) out.z *= ease(p.z - L.z0);
  if (out.y > 0) out.y *= ease(L.y1 - p.y);
  return out;
}

/** The point moved back inside the limit (a share link, an eased move, an orbit zoom); unchanged inside. */
export function clampToLimit(p, L) {
  if (!L) return { ...p };
  return {
    x: Math.min(L.x1, Math.max(L.x0, p.x)),
    y: Math.min(L.y1, p.y),
    z: Math.min(L.z1, Math.max(L.z0, p.z)),
  };
}
