// Pure. Where a camera move to a place ends: the orbit target on the real ground, the camera above
// the ground (or roof) under it. No DOM and no three: points are plain { x, y, z }.

/** Metres the camera keeps above the highest surface under it at the end of a move. */
export const CLEARANCE = 3;
const NUDGE = 0.25; // a target this close to the ground is left where it is

/**
 * The pose a move to a place should end in, once the ground is known. `groundTarget`: the highest
 * surface under the target, `groundCamera`: under the camera (null when unknown). A target off the
 * ground (it was set on a fallback height while the tiles were loading) moves to the ground and the
 * camera moves with it, so the framing stays; then a camera below `groundCamera + CLEARANCE` is lifted.
 * Returns the new { position, target }, or null when the pose is fine as it is.
 */
export function landPose({ position, target }, groundTarget, groundCamera, clearance = CLEARANCE) {
  const p = { ...position }, t = { ...target };
  let changed = false;
  if (Number.isFinite(groundTarget) && Math.abs(groundTarget - t.y) > NUDGE) {
    const dy = groundTarget - t.y; t.y += dy; p.y += dy; changed = true;
  }
  if (Number.isFinite(groundCamera) && p.y < groundCamera + clearance) { p.y = groundCamera + clearance; changed = true; }
  return changed ? { position: p, target: t } : null;
}

/** Wider than this (metres, x or z) a mesh is far-field ground, not campus. */
export const FAR_FIELD = 1000;
/**
 * Does a mesh of this world size ({ x, y, z }) count toward the campus box (`app.bounds`), whose floor is
 * the fallback ground height and the base of the overview? Far-field ground does not: it dips far below.
 */
export function inCampusBox(size) {
  return Math.max(size.x, size.z) <= FAR_FIELD;
}
