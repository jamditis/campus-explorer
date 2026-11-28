// Pure maths for viewer/follow.js: phone compass and tilt to a view direction, and GPS fixes to a
// smooth walking position. No imports, so node --test can run it without three or a DOM.

const DEG = Math.PI / 180;

/**
 * Magnetic declination on the campus, degrees (negative: magnetic north is west of true north).
 * WMM2025 at 40.8625 N, 74.198 W for late 2026: -12.40 (pygeomag 1.1.0, WMM_2025.COF). It drifts about
 * +0.04 degrees a year. Phone compasses report magnetic north, so true = magnetic + DECLINATION.
 */
export const DECLINATION = -12.4;

/** Angle in degrees to [0, 360). */
export function wrap360(deg) {
  const r = deg % 360;
  return r < 0 ? r + 360 : r;
}

/** Signed shortest turn from angle a to angle b, degrees in (-180, 180]. */
export function angleDiff(a, b) {
  const d = wrap360(b - a);
  return d > 180 ? d - 360 : d;
}

/**
 * Where the phone looks, from DeviceOrientation angles in degrees (W3C: alpha about the up axis,
 * counterclockwise seen from above, 0 with the top of the phone to the reference north; beta about
 * the phone's x axis; gamma about its y axis). Returns { heading, pitch, flat } where heading is degrees
 * clockwise from the reference north and pitch is degrees above the horizon.
 *
 * Held up, the view follows the back of the phone (where its camera looks). Held flat, the back points at
 * the ground and has no useful heading, so the heading follows the top edge and `flat` is true.
 */
export function phoneView(alpha, beta, gamma) {
  const a = alpha * DEG, b = beta * DEG, g = gamma * DEG;
  const sA = Math.sin(a), cA = Math.cos(a), sB = Math.sin(b), cB = Math.cos(b), sG = Math.sin(g), cG = Math.cos(g);
  // the phone's -z axis (out of its back) in the earth frame (x east, y north, z up): minus the
  // third column of the W3C rotation matrix Rz(alpha) Rx(beta) Ry(gamma)
  const east = -(cG * sA * sB + cA * sG), north = -(sA * sG - cA * cG * sB), up = -cB * cG;
  const pitch = Math.asin(Math.max(-1, Math.min(1, up))) / DEG;
  if (Math.abs(up) < 0.8) return { heading: wrap360(Math.atan2(east, north) / DEG), pitch, flat: false };
  // the phone's +y axis (its top edge): the second column
  return { heading: wrap360(Math.atan2(-cB * sA, cA * cB) / DEG), pitch, flat: true };
}

/**
 * The compass reading the browser gives for an orientation event, degrees clockwise from magnetic north,
 * or null when it has none. `webkitCompassHeading` (iOS Safari) is already a heading; an absolute event
 * (Android `deviceorientationabsolute`) has alpha counterclockwise from north.
 */
export function compassOf(e) {
  if (typeof e.webkitCompassHeading === 'number' && e.webkitCompassHeading >= 0) return e.webkitCompassHeading;
  if (e.absolute && typeof e.alpha === 'number') return wrap360(360 - e.alpha);
  return null;
}

/**
 * Ease an angle toward a target along the shortest turn. `rate` is per second; `dt` in seconds.
 * Small differences ease more slowly (half rate under `still` degrees), so a phone held still does not shimmer.
 */
export function easeAngle(current, target, dt, rate = 10, still = 1.5) {
  if (current === null || !isFinite(current)) return wrap360(target);
  const d = angleDiff(current, target);
  const r = Math.abs(d) < still ? rate * 0.5 : rate;
  return wrap360(current + d * (1 - Math.exp(-dt * r)));
}

/**
 * Viewer yaw in radians for a true bearing, given the grid convergence at the campus (degrees, grid north
 * east of true north). The walk camera looks along (-sin yaw, 0, -cos yaw) and -z is grid north.
 */
export function yawForBearing(trueDeg, convergence) {
  return -(trueDeg - convergence) * DEG;
}

/**
 * A constant-velocity Kalman filter per axis over GPS fixes in viewer metres. Walking changes speed and
 * direction, so the model lets the velocity wander by `accel` m/s² (noise). Each fix's variance is its
 * reported accuracy squared (the browser's 68 % radius, taken as one sigma).
 */
export function createTrack(accel = 1.2) {
  let s = null; // { t, x: [pos, vel, Ppp, Ppv, Pvv], z: [...] }
  const q = accel * accel;
  function axis(st, dt, m, r) {
    let [p, v, pp, pv, vv] = st;
    // predict
    p += v * dt;
    pp += dt * (2 * pv + dt * vv) + q * dt ** 4 / 4;
    pv += dt * vv + q * dt ** 3 / 2;
    vv += q * dt * dt;
    // update with the measured position
    const k0 = pp / (pp + r), k1 = pv / (pp + r), y = m - p;
    p += k0 * y; v += k1 * y;
    vv -= k1 * pv; pv -= k0 * pv; pp -= k0 * pp;
    return [p, v, pp, pv, vv];
  }
  return {
    /** Add a fix at time `t` (seconds), position (x, z) in metres, accuracy radius in metres. */
    add(t, x, z, accuracy) {
      const r = Math.max(1, accuracy) ** 2;
      if (!s || t - s.t > 30) { s = { t, x: [x, 0, r, 0, 4], z: [z, 0, r, 0, 4] }; return this.state(); }
      const dt = Math.max(0, Math.min(5, t - s.t));
      s = { t, x: axis(s.x, dt, x, r), z: axis(s.z, dt, z, r) };
      return this.state();
    },
    /** Best estimate { x, z, vx, vz, sigma } (sigma: one-sigma radius in metres), or null before a fix. */
    state() {
      if (!s) return null;
      return { x: s.x[0], z: s.z[0], vx: s.x[1], vz: s.z[1], sigma: Math.sqrt((s.x[2] + s.z[2]) / 2) };
    },
    reset() { s = null; },
  };
}

/**
 * Whether (x, z) is on the campus: inside the box { x0, x1, z0, z1 } grown by `margin` metres.
 * Returns { on, distance } where distance is metres outside the grown box (0 when on).
 */
export function campusCheck(x, z, box, margin = 150) {
  const dx = Math.max(box.x0 - margin - x, 0, x - box.x1 - margin);
  const dz = Math.max(box.z0 - margin - z, 0, z - box.z1 - margin);
  const distance = Math.hypot(dx, dz);
  return { on: distance === 0, distance };
}
