// The night sky for an instant and a place: sidereal time, the turn from star coordinates to the
// local horizon, the moon's position and lit fraction, and star brightness and colour. Pure, no
// imports from three. The moon uses the low-precision series of the Astronomical Almanac (about
// 0.3 degrees), which is plenty for a disc half a degree wide drawn over a campus model.

const DEG = Math.PI / 180;
const sinD = d => Math.sin(d * DEG);
const cosD = d => Math.cos(d * DEG);
const wrap = d => ((d % 360) + 360) % 360;

/** Days since J2000.0 (2000-01-01 12:00 UT) of a JS Date. */
export const daysJ2000 = date => date.getTime() / 86400000 - 10957.5;

/** Greenwich mean sidereal time in degrees (IAU 1982, as in Meeus 12.4). */
export function gmstDeg(date) {
  const d = daysJ2000(date), t = d / 36525;
  return wrap(280.46061837 + 360.98564736629 * d + t * t * (0.000387933 - t / 38710000));
}

/**
 * The rotation that takes a J2000 equatorial unit vector [cos(dec) cos(ra), cos(dec) sin(ra), sin(dec)]
 * to local [east, north, up] at an instant and a place. Row-major 3 x 3, as a flat array of 9.
 * Precession since J2000 (about 0.3 degrees by 2026) is left out.
 */
export function equatorialToHorizon(date, lat, lon) {
  const lst = gmstDeg(date) + lon;
  const sl = sinD(lst), cl = cosD(lst), sp = sinD(lat), cp = cosD(lat);
  return [
    -sl, cl, 0,
    -sp * cl, -sp * sl, cp,
    cp * cl, cp * sl, sp,
  ];
}

/** Azimuth (degrees clockwise from true north) and elevation of a right ascension and declination. */
export function altAz(ra, dec, date, lat, lon) {
  const m = equatorialToHorizon(date, lat, lon);
  const v = [cosD(dec) * cosD(ra), cosD(dec) * sinD(ra), sinD(dec)];
  const e = m[0] * v[0] + m[1] * v[1] + m[2] * v[2];
  const n = m[3] * v[0] + m[4] * v[1] + m[5] * v[2];
  const u = m[6] * v[0] + m[7] * v[1] + m[8] * v[2];
  return { azimuth: wrap(Math.atan2(e, n) / DEG), elevation: Math.asin(Math.max(-1, Math.min(1, u))) / DEG };
}

/** The sun's apparent ecliptic longitude in degrees (low precision, about 0.01 degrees). */
function sunLongitude(t) {
  const g = 357.528 + 35999.05 * t;
  return wrap(280.46 + 36000.771 * t + 1.915 * sinD(g) + 0.02 * sinD(2 * g));
}

/**
 * The moon seen from a place.
 * @returns {{ azimuth: number, elevation: number, fraction: number, ra: number, dec: number }}
 *   degrees; elevation is topocentric (corrected for the moon's parallax, up to about 1 degree);
 *   fraction is the lit part of the disc, 0 at new moon and 1 at full.
 */
export function moonPosition(date, lat, lon) {
  const t = daysJ2000(date) / 36525;
  const lambda = 218.32 + 481267.881 * t
    + 6.29 * sinD(134.9 + 477198.85 * t) - 1.27 * sinD(259.2 - 413335.38 * t)
    + 0.66 * sinD(235.7 + 890534.23 * t) + 0.21 * sinD(269.9 + 954397.7 * t)
    - 0.19 * sinD(357.5 + 35999.05 * t) - 0.11 * sinD(186.6 + 966404.05 * t);
  const beta = 5.13 * sinD(93.3 + 483202.03 * t) + 0.28 * sinD(228.2 + 960400.87 * t)
    - 0.28 * sinD(318.3 + 6003.18 * t) - 0.17 * sinD(217.6 - 407332.2 * t);
  const parallax = 0.9508 + 0.0518 * cosD(134.9 + 477198.85 * t) + 0.0095 * cosD(259.2 - 413335.38 * t)
    + 0.0078 * cosD(235.7 + 890534.23 * t) + 0.0028 * cosD(269.9 + 954397.7 * t);
  const eps = 23.439 - 0.013 * t;
  const l = cosD(beta) * cosD(lambda);
  const m = cosD(eps) * cosD(beta) * sinD(lambda) - sinD(eps) * sinD(beta);
  const n = sinD(eps) * cosD(beta) * sinD(lambda) + cosD(eps) * sinD(beta);
  const ra = wrap(Math.atan2(m, l) / DEG), dec = Math.asin(n) / DEG;
  const { azimuth, elevation } = altAz(ra, dec, date, lat, lon);
  // elongation from the sun; the phase angle is very nearly its supplement
  const cosPsi = cosD(beta) * cosD(lambda - sunLongitude(t));
  return {
    azimuth,
    elevation: elevation - Math.asin(sinD(parallax) * cosD(elevation)) / DEG,
    fraction: (1 - cosPsi) / 2,
    ra, dec,
  };
}

/**
 * How bright a star is drawn, 0 to 1, relative to the brightest. Brightness follows the magnitude scale
 * (a factor of 2.512 per magnitude), compressed by `gamma` so faint stars stay visible as points.
 */
export function starBrightness(vmag, { brightest = -1.5, gamma = 0.5 } = {}) {
  return Math.min(1, Math.pow(10, -0.4 * (vmag - brightest)) ** gamma);
}

/**
 * Approximate linear RGB (peak 1) of a star from its B-V colour index: Ballesteros' formula for the
 * temperature, then a black body's colour after Tanner Helland's fit, kept pale (stars look nearly
 * white to the eye).
 */
export function starColor(bv) {
  const b = Math.max(-0.4, Math.min(2, bv));
  const k = 4600 * (1 / (0.92 * b + 1.7) + 1 / (0.92 * b + 0.62)) / 100;
  const r = k <= 66 ? 255 : 329.698727446 * Math.pow(k - 60, -0.1332047592);
  const g = k <= 66 ? 99.4708025861 * Math.log(k) - 161.1195681661 : 288.1221695283 * Math.pow(k - 60, -0.0755148492);
  const bl = k >= 66 ? 255 : k <= 19 ? 0 : 138.5177312231 * Math.log(k - 10) - 305.0447927307;
  const c = [r, g, bl].map(x => Math.max(0, Math.min(255, x)) / 255);
  const peak = Math.max(...c);
  return c.map(x => 0.55 + 0.45 * (x / peak)); // pale: halfway to white
}

/** How much of the starlight shows, 0 to 1: from about civil dusk (sun 4 degrees down) until all are out (12 down). */
export function starsShown(sunElevation) {
  const t = Math.min(1, Math.max(0, (sunElevation + 12) / 8));
  return 1 - t * t * (3 - 2 * t);
}

/**
 * How strong the night sky's light dome is toward a bearing (degrees from true north), as the sky shader in look.js
 * draws it: a broad glow toward Midtown Manhattan (124 degrees), a bright core over it and a weaker one over Newark
 * and its airport (168 degrees), so the two cities show as two peaks with a dip between. About 1 toward Manhattan.
 */
export function domeShape(bearing) {
  const c = d => Math.max(Math.cos((bearing - d) * Math.PI / 180), 0);
  return 0.5 * c(124) ** 1.5 + 0.5 * c(124) ** 20 + 0.45 * c(168) ** 20;
}
