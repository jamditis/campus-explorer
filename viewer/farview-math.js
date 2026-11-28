// The far view's tree canopy (viewer/canopy.webp, built by tools/farview/build_canopy.py from the USFS Tree
// Canopy Cover): where the map lies in the viewer frame, and how a cover share becomes visible crowns. Pure,
// no imports from three; look.js draws it.

/** The canopy map: file and its box in viewer metres [x0, z0, x1, z1] (canopy.json's Blender box, y north -> -z). */
export const CANOPY = { file: './viewer/canopy.webp', box: [-10000, -10000, 21980, 20000] };

/** Map coordinates (0 to 1, row 0 north) of a viewer point, or null outside the map. */
export function canopyUv(x, z, box = CANOPY.box) {
  const u = (x - box[0]) / (box[2] - box[0]), v = (z - box[1]) / (box[3] - box[1]);
  return u < 0 || v < 0 || u > 1 || v > 1 ? null : [u, v];
}

// The shader's hash and value noise, mirrored so the crown pattern's spread can be measured here
const fract = x => x - Math.floor(x);
export const caHash = (x, y) => fract(Math.sin(x * 127.1 + y * 311.7) * 43758.5453);
function valueNoise(x, y) {
  const ix = Math.floor(x), iy = Math.floor(y);
  let fx = x - ix, fy = y - iy;
  fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
  const a = caHash(ix, iy), b = caHash(ix + 1, iy), c = caHash(ix, iy + 1), d = caHash(ix + 1, iy + 1);
  const top = a + (b - a) * fx;
  return top + (c + (d - c) * fx - top) * fy;
}

/** Crown noise at a ground point (viewer x, z): two octaves of value noise at 9 m, rounded crowns, 0 to 1. */
export function crownNoise(x, z) {
  const qx = x / 9, qz = z / 9;
  return 0.65 * valueNoise(qx, qz) + 0.35 * valueNoise(qx * 2.7 + 13.1, qz * 2.7 + 13.1);
}

/**
 * crownNoise's quantiles at every 5 % (measured over 8.3 million points, 40 km square): value noise bunches
 * round 0.5, so the threshold for a cover share comes from these, not from 1 - cover.
 */
export const NOISE_Q = [0.0083, 0.2397, 0.2908, 0.3277, 0.3583, 0.3854, 0.4103, 0.4337, 0.4563, 0.4783, 0.5001, 0.5218, 0.5438, 0.5664, 0.5899, 0.6148, 0.6419, 0.6724, 0.7093, 0.7603, 0.9918];

/** The noise value below which a share `u` (0 to 1) of the ground lies: NOISE_Q, linear between steps. */
export function noiseQuantile(u) {
  const t = Math.min(1, Math.max(0, u)) * 20, i = Math.min(19, Math.floor(t));
  return NOISE_Q[i] + (NOISE_Q[i + 1] - NOISE_Q[i]) * (t - i);
}

/**
 * Share of a ground pixel drawn as tree crown, 0 to 1. `cover` is the map's canopy share, `n` the crown noise
 * there and `detail` how much of that noise a pixel can still show (0 far, 1 near). Near, crowns are where the
 * noise is above its (1 - cover) quantile, so the covered area matches the map; far, the pixel takes the cover
 * share itself. Mirrors the canopy chunk in look.js.
 */
export function crownShare(cover, n, detail) {
  if (cover <= 0) return 0;
  if (cover >= 1) return 1;
  const s = 0.02, x = Math.min(1, Math.max(0, (n - noiseQuantile(1 - cover) + s) / (2 * s)));
  return x * x * (3 - 2 * x) * detail + cover * (1 - detail);
}

/**
 * Lit tower tops on the skyline after dark: real landmarks whose tops are lit every night. Colours are a plain
 * white or warm white (UNVERIFIED: the Empire State Building's lights change colour for events).
 */
export const LANDMARKS = [
  { name: 'Empire State Building', lat: 40.74844, lon: -73.98566, color: [1, 0.93, 0.8] },
  { name: 'One World Trade Center', lat: 40.71274, lon: -74.01338, color: [0.95, 0.97, 1] },
  { name: 'Chrysler Building', lat: 40.75162, lon: -73.97545, color: [0.95, 0.95, 1] },
];

/**
 * The highest point of the skyline stand-in within `tolDeg` of a bearing seen from the campus origin, from its
 * world positions (x, y, z, ...): where a tower's top light goes. Bearing in degrees, grid (atan2(x, -z)).
 * @returns {number[]|null} [x, y, z]
 */
export function towerTop(pos, bearingDeg, tolDeg = 0.06) {
  let best = -1, top = -Infinity;
  for (let i = 0; i < pos.length; i += 3) {
    const b = Math.atan2(pos[i], -pos[i + 2]) * 180 / Math.PI;
    if (Math.abs(((b - bearingDeg + 540) % 360) - 180) <= tolDeg && pos[i + 1] > top) { top = pos[i + 1]; best = i; }
  }
  return best < 0 ? null : [pos[best], pos[best + 1], pos[best + 2]];
}
