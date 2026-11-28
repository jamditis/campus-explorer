// Pure. Where the sun's shadow box sits (look.js update): centred on what you look at, sized to the view distance
// in steps, and moved only when it must, because every move redraws the whole shadow map.

/** Share of the box's half-width the focus may drift from the box centre before the box follows. */
export const SHADOW_SLACK = 1 / 16;

/** Half-width of the area that must have shadows, metres: 0.9 x the view distance, 45 to 700 m, in steps of 1.25. */
export function shadowHalf(dist) {
  const raw = Math.min(700, Math.max(45, dist * 0.9));
  return 45 * Math.pow(1.25, Math.round(Math.log(raw / 45) / Math.log(1.25)));
}

/** Half-width of the shadow camera: the area plus the slack, so it is covered wherever in the slack the focus is. */
export const shadowReach = half => half * (1 + SHADOW_SLACK);

/**
 * Whether the box moves to `focus` ({ x, y, z }, already snapped) from `last` (its centre, or null at first).
 * It moves when the area changes size, when the focus drifts past the slack or changes height step, or when
 * the shadow map is redrawn anyway (`dirty`), which costs nothing extra.
 */
export function shadowMoves(focus, last, half, lastHalf, dirty) {
  if (!last || half !== lastHalf || dirty || focus.y !== last.y) return true;
  return Math.max(Math.abs(focus.x - last.x), Math.abs(focus.z - last.z)) > half * SHADOW_SLACK;
}
