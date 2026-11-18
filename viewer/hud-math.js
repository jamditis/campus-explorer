// Pure maths for viewer/hud.js: scale bar lengths, minimap pixel <-> world, north-facing poses and
// the tone mapping the minimap needs. No imports, so node --test can run it without three or a DOM.

const DEG = Math.PI / 180;
const FT = 0.3048;

/** Ground metres covered by one CSS pixel at `distance` metres from a perspective camera. */
export function metresPerPixel(distance, fovDeg, heightPx) {
  return (2 * distance * Math.tan((fovDeg * DEG) / 2)) / Math.max(1, heightPx);
}

/**
 * A round scale-bar length (1, 2 or 5 × 10^n metres) for `mpp` metres per pixel. Picks the one
 * whose bar falls in [minPx, maxPx]; when none does (1-2-5 steps are up to 2.5× apart), the one
 * nearest the range. Returns { metres, px }.
 */
export function niceScale(mpp, minPx = 60, maxPx = 140) {
  if (!(mpp > 0) || !isFinite(mpp)) return { metres: 0, px: 0 };
  let best = null, bestMiss = Infinity;
  const start = Math.floor(Math.log10(minPx * mpp)) - 1;
  for (let e = start; e <= start + 3; e++) {
    for (const m of [1, 2, 5]) {
      const metres = m * 10 ** e, px = metres / mpp;
      const miss = px < minPx ? minPx / px : px > maxPx ? px / maxPx : 1;
      if (miss < bestMiss - 1e-9) { best = { metres: roundSig(metres), px }; bestMiss = miss; }
    }
  }
  return best;
}

function roundSig(v) { return Number(v.toPrecision(6)); }

/** Scale-bar label such as `50 m · 164 ft` or `2 km · 1.24 mi`. */
export function formatScale(metres) {
  if (metres >= 1000) return `${roundSig(metres / 1000)} km · ${(metres / 1609.344).toFixed(2)} mi`;
  const ft = metres / FT;
  return `${roundSig(metres)} m · ${ft < 10 ? ft.toFixed(1) : Math.round(ft)} ft`;
}

/** NAVD88 metres to text such as `132.4 m · 434 ft NAVD88`. */
export function formatElevation(y) {
  return `${y.toFixed(1)} m · ${Math.round(y / FT)} ft NAVD88`;
}

/**
 * The square map extent around a box (x and z), grown by `pad` (0.05 = 5%).
 * Returns { x0, z0, size }: x0, z0 is the north-west corner (smallest x and z), size in metres.
 */
export function mapExtent(minX, minZ, maxX, maxZ, pad = 0.05) {
  const cx = (minX + maxX) / 2, cz = (minZ + maxZ) / 2;
  const size = Math.max(maxX - minX, maxZ - minZ, 1) * (1 + pad);
  return { x0: cx - size / 2, z0: cz - size / 2, size };
}

/** World x, z to map pixels for a `px`-wide map drawn north (-Z) up. */
export function worldToMap(x, z, ext, px) {
  return { u: ((x - ext.x0) / ext.size) * px, v: ((z - ext.z0) / ext.size) * px };
}

/** Map pixels back to world x, z. */
export function mapToWorld(u, v, ext, px) {
  return { x: ext.x0 + (u / px) * ext.size, z: ext.z0 + (v / px) * ext.size };
}

/**
 * Camera offset from the orbit target that looks due true north, keeping horizontal distance
 * `r`. Grid north (-Z) is `convDeg` east of true north, so true north is at grid bearing -convDeg.
 */
export function northOffset(r, convDeg) {
  const b = -convDeg * DEG;
  return { dx: -Math.sin(b) * r, dz: Math.cos(b) * r };
}

/** Player yaw (radians, see viewer/player.js: forward = (-sin yaw, 0, -cos yaw)) that faces true north. */
export function northYaw(convDeg) {
  return convDeg * DEG; // grid bearing = -yaw, true bearing = grid bearing + convergence
}

/** Horizontal field of view in degrees from the vertical one and the aspect ratio. */
export function horizontalFov(fovDeg, aspect) {
  return (2 * Math.atan(Math.tan((fovDeg * DEG) / 2) * aspect)) / DEG;
}

/** Compass readout such as `SW 225°`, given the 16-point name for the bearing. */
export function headingLabel(deg, point) {
  const d = Math.round(((deg % 360) + 360) % 360) % 360;
  return `${point} ${d}°`;
}

/**
 * Linear scene colour to display sRGB bytes the way the main view draws it: exposure, three.js's
 * ACES filmic fit, then the sRGB transfer curve. Render targets skip both steps in three.js, so the
 * minimap does them here. Writes [r, g, b] (0 to 255) into `out`.
 */
export function toneMapToSrgb(r, g, b, exposure, out) {
  const k = exposure / 0.6;
  r *= k; g *= k; b *= k;
  const ir = 0.59719 * r + 0.35458 * g + 0.04823 * b;
  const ig = 0.076 * r + 0.90834 * g + 0.01566 * b;
  const ib = 0.0284 * r + 0.13383 * g + 0.83777 * b;
  const fr = rrt(ir), fg = rrt(ig), fb = rrt(ib);
  out[0] = srgbByte(1.60475 * fr - 0.53108 * fg - 0.07367 * fb);
  out[1] = srgbByte(-0.10208 * fr + 1.10813 * fg - 0.00605 * fb);
  out[2] = srgbByte(-0.00327 * fr - 0.07276 * fg + 1.07602 * fb);
  return out;
}

function rrt(v) {
  return (v * (v + 0.0245786) - 0.000090537) / (v * (0.983729 * v + 0.432951) + 0.238081);
}

function srgbByte(c) {
  c = c <= 0 ? 0 : c >= 1 ? 1 : c;
  const s = c <= 0.0031308 ? c * 12.92 : 1.055 * c ** (1 / 2.4) - 0.055;
  return Math.round(s * 255);
}
