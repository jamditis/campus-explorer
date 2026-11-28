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

/**
 * Share of a ground pixel drawn as tree crown, 0 to 1. `cover` is the map's canopy share, `n` a noise value
 * (0 to 1, spread evenly) at crown scale and `detail` how much of that noise a pixel can still show (0 far, 1
 * near). Near, crowns are where the noise is above 1 - cover, so the covered area matches the map; far, the
 * pixel takes the cover share itself. Mirrors the canopy chunk in look.js.
 */
export function crownShare(cover, n, detail) {
  const s = 0.12, lo = 1 - cover - s, x = Math.min(1, Math.max(0, (n - lo) / (2 * s)));
  const crowns = cover <= 0 ? 0 : cover >= 1 ? 1 : x * x * (3 - 2 * x);
  return crowns * detail + cover * (1 - detail);
}

// The shader's hash, mirrored so the crown noise's spread can be checked here
const fract = x => x - Math.floor(x);
export const caHash = (x, y) => fract(Math.sin(x * 127.1 + y * 311.7) * 43758.5453);

/**
 * Crown noise at a ground point (viewer x, z), 0 to 1, as the canopy chunk computes it: one evenly spread
 * random value per 9 m cell (so thresholding at 1 - cover covers the cover share), its edges broken by
 * +-0.07 of finer noise. Value noise alone bunches round 0.5 and covered too little of thin canopy.
 */
export function crownNoise(x, z) {
  const qx = x / 9, qz = z / 9;
  const wob = caHash(Math.floor(qx * 2.3 + 5.1), Math.floor(qz * 2.3 + 5.1)) - 0.5;
  return Math.min(1, Math.max(0, caHash(Math.floor(qx), Math.floor(qz)) + 0.14 * wob));
}
