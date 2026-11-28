// Pure. Entrance doors that open in walk mode (#119). The build marks each moving leaf: an object named
// DOOR_<building>_<entrance>_<leaf> with extras `door` in Blender world axes ({ id, building, kind: 'swing' |
// 'slide', hinge: [x, y, z], axis: [x, y, z], open: degrees, travel: [dx, dy, dz] }). Here: those extras in viewer
// axes, when a door opens or closes for the walker, how far it is open over time, and where a leaf then sits.
// No DOM and no three: points are arrays or { x, y, z }, matrices 16 numbers, column-major.

/** Metres: a door opens for a walker this near who faces it, and closes once the walker is this far. */
export const DOOR_NEAR = 3, DOOR_FAR = 4.5;
/** Seconds a door takes to open or close. */
export const DOOR_TIME = 0.6;
/** The walker faces a door when it lies within this many degrees of the way they look. */
export const DOOR_FACING = 70;
/** A door at least this far open (0 to 1) lets the walker through. */
export const DOOR_PASS = 0.6;

/** Blender world axes to viewer axes: x east, y up, z south. */
export const toViewer = ([x, y, z]) => [x, z, -y || 0];

const num3 = a => Array.isArray(a) && a.length === 3 && a.every(Number.isFinite);

/** A door from a leaf's extras, in viewer axes and radians, or null when the extras are not a usable door. */
export function doorFrom(e) {
  if (!e || typeof e.id !== 'string' || !e.id) return null;
  if (e.kind === 'slide') {
    if (!num3(e.travel)) return null;
    return { id: e.id, building: String(e.building ?? ''), kind: 'slide', travel: toViewer(e.travel) };
  }
  if (e.kind !== 'swing' || !num3(e.hinge) || !num3(e.axis) || !Number.isFinite(e.open)) return null;
  const a = toViewer(e.axis), l = Math.hypot(...a);
  if (l < 1e-6) return null;
  return { id: e.id, building: String(e.building ?? ''), kind: 'swing', hinge: toViewer(e.hinge), axis: a.map(v => v / l), open: e.open * Math.PI / 180 };
}

/**
 * Whether a door should be open: the walker (`p`, feet) within DOOR_NEAR of its middle `at`, on about the same
 * level and facing it (`look`: { x, z } the way they look), or, once it is open, still within DOOR_FAR.
 */
export function wantsOpen(at, p, look, open) {
  const dx = at.x - p.x, dz = at.z - p.z, d = Math.hypot(dx, dz);
  if (Math.abs(at.y - p.y) > 2.5) return false;
  if (open) return d <= DOOR_FAR;
  if (d > DOOR_NEAR) return false;
  if (d < 0.5) return true; // in the doorway itself
  const l = Math.hypot(look.x, look.z) || 1;
  return (dx * look.x + dz * look.z) / (d * l) >= Math.cos(DOOR_FACING * Math.PI / 180);
}

/** How far open (0 to 1) after `dt` seconds moving toward `want`. */
export const stepOpen = (s, want, dt) => Math.min(1, Math.max(0, s + (want ? 1 : -1) * dt / DOOR_TIME));

const ease = s => s * s * (3 - 2 * s);

/** The move (a matrix to put before the leaf's own world matrix) of a door `s` open (0 to 1). */
export function leafMove(door, s) {
  const k = ease(Math.min(1, Math.max(0, s)));
  if (door.kind === 'slide') { const [x, y, z] = door.travel; return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, x * k, y * k, z * k, 1]; }
  const [ux, uy, uz] = door.axis, t = door.open * k, c = Math.cos(t), sn = Math.sin(t), C = 1 - c;
  // rotation about the axis through the hinge: R, then the hinge kept where it is (p' = R (p - h) + h)
  const R = [
    c + ux * ux * C, uy * ux * C + uz * sn, uz * ux * C - uy * sn,
    ux * uy * C - uz * sn, c + uy * uy * C, uz * uy * C + ux * sn,
    ux * uz * C + uy * sn, uy * uz * C - ux * sn, c + uz * uz * C,
  ];
  const [hx, hy, hz] = door.hinge;
  const tx = hx - (R[0] * hx + R[3] * hy + R[6] * hz), ty = hy - (R[1] * hx + R[4] * hy + R[7] * hz), tz = hz - (R[2] * hx + R[5] * hy + R[8] * hz);
  return [R[0], R[1], R[2], 0, R[3], R[4], R[5], 0, R[6], R[7], R[8], 0, tx, ty, tz, 1];
}
