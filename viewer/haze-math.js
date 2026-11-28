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

/** three.js ACESFilmicToneMapping (r170) for one linear RGB colour; `exposure` as renderer.toneMappingExposure. */
export function acesFilmic([r, g, b], exposure = 1) {
  const k = exposure / 0.6;
  r *= k; g *= k; b *= k;
  // ACESInputMat, column-major in the shader
  const i = [0.59719 * r + 0.35458 * g + 0.04823 * b, 0.076 * r + 0.90834 * g + 0.01566 * b, 0.0284 * r + 0.13383 * g + 0.83777 * b];
  const f = i.map(v => (v * (v + 0.0245786) - 0.000090537) / (v * (0.983729 * v + 0.432951) + 0.238081));
  const o = [
    1.60475 * f[0] - 0.53108 * f[1] - 0.07367 * f[2],
    -0.10208 * f[0] + 1.10813 * f[1] - 0.00605 * f[2],
    -0.00327 * f[0] - 0.07276 * f[1] + 1.07602 * f[2],
  ];
  return o.map(v => Math.min(1, Math.max(0, v)));
}

/** Linear to sRGB-encoded, per channel. */
export const toSrgb = rgb => rgb.map(c => (c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055));

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
