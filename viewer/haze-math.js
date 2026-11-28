// Aerial perspective: how much of a surface's own colour survives a distance of haze, and the colour
// the haze takes in each direction, read off the sky itself. Pure, no imports from three; look.js
// does the drawing (the fog chunk) and the sky readback.

/**
 * Share of a surface's colour that survives `d` metres of haze, 0 to 1. Two terms: the near haze the
 * viewer had before (exp(-(density * d)^2), FogExp2), and a slower
 * far haze (amount * exp(-d / far)) that keeps the far ground, the ridges and the skyline faintly in view.
 * The larger of the two wins. Mirrors the fog chunk in look.js.
 */
export function transmittance(d, { density, amount, far }) {
  return Math.max(Math.exp(-((density * d) ** 2)), amount * Math.exp(-d / Math.max(far, 1)));
}

/** transmittance for red, green and blue: the far haze's length is shorter by `rgb` shares in each (look.js HAZE_RGB). */
export const transmittanceRgb = (d, h, rgb) => rgb.map(k => transmittance(d, { ...h, far: h.far * (1 - k) }));

// three.js ACESFilmicToneMapping (r170): its two matrices, row-major here (the shader writes them by column)
export const ACES_IN = [[0.59719, 0.35458, 0.04823], [0.076, 0.90834, 0.01566], [0.0284, 0.13383, 0.83777]];
export const ACES_OUT = [[1.60475, -0.53108, -0.07367], [-0.10208, 1.10813, -0.00605], [-0.00327, -0.07276, 1.07602]];
const mul = (m, v) => m.map(row => row[0] * v[0] + row[1] * v[1] + row[2] * v[2]);

/** The inverse of a 3 x 3 matrix (rows). */
export function invert3(m) {
  const [[a, b, c], [d, e, f], [g, h, i]] = m;
  const A = e * i - f * h, B = f * g - d * i, C = d * h - e * g, det = a * A + b * B + c * C;
  return [
    [A / det, (c * h - b * i) / det, (b * f - c * e) / det],
    [B / det, (a * i - c * g) / det, (c * d - a * f) / det],
    [C / det, (b * g - a * h) / det, (a * e - b * d) / det],
  ];
}

/** three.js ACESFilmicToneMapping (r170) for one linear RGB colour; `exposure` as renderer.toneMappingExposure. */
export function acesFilmic(rgb, exposure = 1) {
  const f = mul(ACES_IN, rgb.map(c => c * exposure / 0.6)).map(v => (v * (v + 0.0245786) - 0.000090537) / (v * (0.983729 * v + 0.432951) + 0.238081));
  return mul(ACES_OUT, f).map(v => Math.min(1, Math.max(0, v)));
}

/**
 * The linear colour that acesFilmic maps to `rgb` (each channel under 1): the fit's quadratic solved for its
 * input, through the inverse matrices. Mirrors the fog chunk's hzIn in look.js.
 */
export function acesFilmicInverse(rgb, exposure = 1) {
  const y = mul(invert3(ACES_OUT), rgb).map(v => Math.min(0.999, Math.max(0, v)));
  const v = y.map(t => {
    const a = 1 - 0.983729 * t, b = 0.0245786 - 0.432951 * t, c = -(0.000090537 + 0.238081 * t);
    return (-b + Math.sqrt(Math.max(b * b - 4 * a * c, 0))) / (2 * a);
  });
  return mul(invert3(ACES_IN), v).map(c => c * 0.6 / exposure);
}

/** Linear to sRGB-encoded, per channel. */
export const toSrgb = rgb => rgb.map(c => (c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055));

/** A 3 x 3 matrix (rows) as a GLSL mat3 literal (by column). */
export const glslMat3 = m => `mat3(${[0, 1, 2].map(j => m.map(row => row[j].toFixed(7)).join(', ')).join(', ')})`;

/**
 * The haze colour from three samples of the sky's horizon (display colours, sRGB 0 to 1): toward the
 * sun, square to it, and away from it. The shader draws away + tint * ((1 + cos a) / 2)^power, a the
 * angle to the sun's bearing; `power` is fitted so that square to the sun matches too (clamped 1 to 16).
 * @returns {{ away: number[], tint: number[], power: number }}
 */
export function hazeColours(toward, side, away) {
  const tint = toward.map((t, i) => t - away[i]);
  const span = tint.reduce((s, t) => s + Math.abs(t), 0);
  let power = 4;
  if (span > 0.01) {
    const share = side.reduce((s, x, i) => s + (x - away[i]) * Math.sign(tint[i]), 0) / span;
    power = share > 0 ? Math.min(16, Math.max(1, Math.log(share) / Math.log(0.5))) : 16;
  }
  return { away, tint, power };
}
