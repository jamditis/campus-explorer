import { test } from 'node:test';
import assert from 'node:assert/strict';
import { transmittance, transmittanceRgb, acesFilmic, acesFilmicInverse, invert3, glslMat3, ACES_IN, toSrgb, hazeColours } from '../viewer/haze-math.js';

const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg ?? ''} ${a} vs ${b}`);
const H = { density: 0.00027, amount: 0.45, far: 16000 };

test('near haze is the old FogExp2; the far term keeps the distance in view', () => {
  for (const d of [0, 500, 1500, 3000]) near(transmittance(d, H), Math.exp(-((0.00027 * d) ** 2)), 1e-12, `${d} m`);
  near(transmittance(10000, { ...H, amount: 0 }), Math.exp(-((2.7) ** 2)), 1e-12);
  // the skyline at 20 km keeps about an eighth of its own colour, a ridge at 6 km about a third
  near(transmittance(20000, H), 0.45 * Math.exp(-1.25), 1e-12);
  assert.ok(transmittance(6000, H) > 0.3 && transmittance(6000, { ...H, amount: 0 }) < 0.1);
  // never rises with distance
  let last = 1;
  for (let d = 0; d <= 33000; d += 250) { const t = transmittance(d, H); assert.ok(t <= last + 1e-12, `${d}`); last = t; }
});

test('ACES filmic: black stays black, grey stays grey, bright saturates', () => {
  for (const c of acesFilmic([0, 0, 0])) near(c, 0, 0.002);
  const g = acesFilmic([0.18, 0.18, 0.18], 0.8);
  near(g[0], g[1], 0.003); near(g[1], g[2], 0.003);
  for (const c of acesFilmic([40, 40, 40])) near(c, 1, 0.02);
  assert.ok(acesFilmic([0.3, 0.3, 0.3])[0] > acesFilmic([0.2, 0.2, 0.2])[0]);
});

test('sRGB encoding', () => {
  const [z, o] = toSrgb([0, 1]); near(z, 0, 1e-12); near(o, 1, 1e-12);
  near(toSrgb([0.214041])[0], 0.5, 1e-4);
});

test('haze colours: the fitted power reproduces the sample square to the sun', () => {
  const toward = [0.9, 0.7, 0.5], away = [0.5, 0.55, 0.65];
  for (const p of [1, 2.5, 6]) {
    const side = toward.map((t, i) => away[i] + (t - away[i]) * 0.5 ** p);
    const h = hazeColours(toward, side, away);
    near(h.power, p, 1e-9);
    assert.deepEqual(h.away, away);
    h.tint.forEach((t, i) => near(t, toward[i] - away[i], 1e-12));
  }
  // an even sky (night, overcast) has no tint to shape
  assert.equal(hazeColours([0.1, 0.1, 0.1], [0.1, 0.1, 0.1], [0.1, 0.1, 0.1]).power, 4);
});

test('per channel: blue clears first, so far ground turns blue-grey', () => {
  const [r, g, b] = transmittanceRgb(20000, { ...H, amount: 0.7, far: 24000 }, [0, 0.33, 0.58]);
  assert.ok(r > g && g > b && b > 0.05, `${r} ${g} ${b}`);
  assert.deepEqual(transmittanceRgb(1000, H, [0, 0.33, 0.58]).map(t => t.toFixed(9)), Array(3).fill(Math.exp(-(0.27 ** 2)).toFixed(9)));
});

test('the inverse ACES undoes ACES, so High can mix haze as the screen does', () => {
  const I = invert3(ACES_IN);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
    near(ACES_IN[i][0] * I[0][j] + ACES_IN[i][1] * I[1][j] + ACES_IN[i][2] * I[2][j], i === j ? 1 : 0, 1e-12);
  }
  for (const c of [[0.03, 0.03, 0.03], [0.2, 0.15, 0.1], [1.34, 1.2, 1.1], [0.004, 0.006, 0.012]]) {
    const back = acesFilmicInverse(acesFilmic(c, 0.8), 0.8);
    back.forEach((x, i) => near(x, c[i], 2e-3 * Math.max(1, c[i]), `${c}`));
  }
  // the reviewer's case: a dark surface at 20 km under a bright horizon mixes to the same screen colour either way
  const fog = [1.34, 1.3, 1.25], dark = [0.03, 0.03, 0.03], t = 0.3;
  const screen = toSrgb(acesFilmic(fog, 0.8)).map((f, i) => f + (toSrgb(acesFilmic(dark, 0.8))[i] - f) * t);
  const high = toSrgb(acesFilmic(acesFilmicInverse(screen.map(d => (d <= 0.04045 ? d / 12.92 : ((d + 0.055) / 1.055) ** 2.4)), 0.8), 0.8));
  high.forEach((x, i) => near(x, screen[i], 2e-3));
  assert.match(glslMat3([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), /^mat3\(1\.0+, 4\.0+, 7\.0+, 2\.0+/);
});
