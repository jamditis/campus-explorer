import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gmstDeg, equatorialToHorizon, altAz, moonPosition, starBrightness, starColor, starsShown } from '../viewer/sky-math.js';
import { sunPosition } from '../viewer/sun.js';

const near = (a, b, tol, msg) => assert.ok(Math.abs(a - b) <= tol, `${msg ?? ''} ${a} vs ${b} (tol ${tol})`);
const angle = (a, b) => Math.abs(((a - b + 540) % 360) - 180);
const MONTCLAIR = [40.8635, -74.1986];

test('sidereal time at J2000.0 and a day later', () => {
  near(gmstDeg(new Date(Date.UTC(2000, 0, 1, 12))), 280.46061837, 1e-6);
  // Meeus example 12.a: 1987 April 10, 0h UT -> 13h10m46.3668s = 197.693195 degrees
  near(gmstDeg(new Date(Date.UTC(1987, 3, 10))), 197.693195, 1e-4);
});

test('the turn to the horizon is a rotation', () => {
  const m = equatorialToHorizon(new Date(Date.UTC(2026, 10, 28, 3)), ...MONTCLAIR);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
    const dot = m[i * 3] * m[j * 3] + m[i * 3 + 1] * m[j * 3 + 1] + m[i * 3 + 2] * m[j * 3 + 2];
    near(dot, i === j ? 1 : 0, 1e-12, `rows ${i},${j}`);
  }
});

test('Polaris stands at the latitude, a little off due north', () => {
  for (const h of [0, 6, 13, 19]) {
    const p = altAz(37.954, 89.264, new Date(Date.UTC(2026, 10, 28, h)), ...MONTCLAIR);
    near(p.elevation, MONTCLAIR[0], 0.8, `hour ${h}`);
    assert.ok(angle(p.azimuth, 0) < 1.1, `azimuth ${p.azimuth}`);
  }
});

test('Sirius culminates due south at 90 - lat + dec', () => {
  // find the highest point over one day, minute by minute
  let best = { elevation: -90 };
  const t0 = Date.UTC(2026, 0, 15);
  for (let k = 0; k < 1440; k++) {
    const p = altAz(101.287, -16.716, new Date(t0 + k * 60000), ...MONTCLAIR);
    if (p.elevation > best.elevation) best = p;
  }
  near(best.elevation, 90 - MONTCLAIR[0] - 16.716, 0.05);
  assert.ok(angle(best.azimuth, 180) < 0.5, `azimuth ${best.azimuth}`);
});

test('the moon covers the sun at the 8 April 2024 total eclipse (Dallas, 18:42 UT)', () => {
  const at = new Date(Date.UTC(2024, 3, 8, 18, 42)), place = [32.78, -96.8];
  const m = moonPosition(at, ...place), s = sunPosition(at, ...place);
  near(m.elevation, s.elevation, 0.6, 'elevation');
  assert.ok(angle(m.azimuth, s.azimuth) < 0.8, `azimuth ${m.azimuth} vs ${s.azimuth}`);
  assert.ok(m.fraction < 0.01, `fraction ${m.fraction}`);
});

test('the lit fraction runs from new to full', () => {
  near(moonPosition(new Date(Date.UTC(2024, 3, 23, 23, 49)), ...MONTCLAIR).fraction, 1, 0.01, 'full 23 April 2024');
  near(moonPosition(new Date(Date.UTC(2024, 3, 15, 19, 13)), ...MONTCLAIR).fraction, 0.5, 0.04, 'first quarter 15 April 2024');
});

test('star brightness and colour', () => {
  assert.equal(starBrightness(-1.5), 1);
  near(starBrightness(1), Math.pow(10, -0.4 * 2.5) ** 0.5, 1e-12);
  assert.ok(starBrightness(4.5) > 0.05 && starBrightness(4.5) < starBrightness(3));
  const blue = starColor(-0.3), red = starColor(1.6), sun = starColor(0.65);
  assert.ok(blue[2] >= blue[0] && red[0] > red[2], 'hot stars blue, cool stars red');
  for (const c of [blue, red, sun]) for (const x of c) assert.ok(x >= 0.55 && x <= 1);
});

test('stars.json: brightest first, every field in range', () => {
  const doc = JSON.parse(readFileSync(new URL('../viewer/stars.json', import.meta.url)));
  assert.deepEqual(doc.fields, ['ra_deg', 'dec_deg', 'vmag', 'b_v']);
  assert.ok(doc.stars.length > 800);
  let last = -Infinity;
  for (const [ra, dec, v] of doc.stars) {
    assert.ok(ra >= 0 && ra < 360 && dec >= -90 && dec <= 90 && v < doc.limit && v >= last);
    last = v;
  }
  assert.deepEqual(doc.stars[0].slice(0, 3), [101.287, -16.716, -1.46]); // Sirius
});

test('stars fade in from civil dusk to nautical dusk', () => {
  assert.equal(starsShown(10), 0);
  assert.equal(starsShown(-4), 0);
  assert.equal(starsShown(-12), 1);
  assert.equal(starsShown(-40), 1);
  near(starsShown(-8), 0.5, 1e-12);
});
