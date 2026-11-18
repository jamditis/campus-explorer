// Pure coordinate maths for the campus model. No imports, so node --test can run it.
//
// Frames:
//   EPSG:6527  NAD83(2011) / New Jersey, US survey feet (Transverse Mercator on GRS80)
//   Blender    x = (E - E0) * M_PER_FTUS, y = (N - N0) * M_PER_FTUS, metres, +y grid north
//   three.js   x = Blender x (east), z = -Blender y (so -z is grid north), y up
//
// The projection uses the Krüger series to sixth order in n (Karney 2011), which is
// accurate to well under a millimetre this close to the central meridian.

/** Metres per US survey foot (exact by definition). */
export const M_PER_FTUS = 1200 / 3937;

/** Local origin of the model in EPSG:6527 US survey feet. */
export const ORIGIN = Object.freeze({ E0: 575880, N0: 738340 });

const DEG = Math.PI / 180;

// GRS80 ellipsoid and the New Jersey state plane zone parameters.
const A_AXIS = 6378137;
const FLAT = 1 / 298.257222101;
const K0 = 0.9999;
const LAT0 = (38 + 50 / 60) * DEG;
const LON0 = -74.5 * DEG;
const FALSE_E = 150000;
const FALSE_N = 0;

const E2 = FLAT * (2 - FLAT);
const ECC = Math.sqrt(E2);
const N3 = FLAT / (2 - FLAT);

const RECT_A = (A_AXIS / (1 + N3)) *
  (1 + N3 ** 2 / 4 + N3 ** 4 / 64 + N3 ** 6 / 256);

const ALPHA = krugerCoefficients(N3, [
  [1 / 2, -2 / 3, 5 / 16, 41 / 180, -127 / 288, 7891 / 37800],
  [0, 13 / 48, -3 / 5, 557 / 1440, 281 / 630, -1983433 / 1935360],
  [0, 0, 61 / 240, -103 / 140, 15061 / 26880, 167603 / 181440],
  [0, 0, 0, 49561 / 161280, -179 / 168, 6601661 / 7257600],
  [0, 0, 0, 0, 34729 / 80640, -3418889 / 1995840],
  [0, 0, 0, 0, 0, 212378941 / 319334400],
]);

const BETA = krugerCoefficients(N3, [
  [1 / 2, -2 / 3, 37 / 96, -1 / 360, -81 / 512, 96199 / 604800],
  [0, 1 / 48, 1 / 15, -437 / 1440, 46 / 105, -1118711 / 3870720],
  [0, 0, 17 / 480, -37 / 840, -209 / 4480, 5569 / 90720],
  [0, 0, 0, 4397 / 161280, -11 / 504, -830251 / 7257600],
  [0, 0, 0, 0, 4583 / 161280, -108847 / 3991680],
  [0, 0, 0, 0, 0, 20648693 / 638668800],
]);

function krugerCoefficients(n, rows) {
  return rows.map((row) => row.reduce((sum, c, i) => sum + c * n ** (i + 1), 0));
}

// Conformal latitude as tan, from geodetic latitude as tan.
function tauPrime(tau) {
  const sigma = Math.sinh(ECC * Math.atanh(ECC * tau / Math.hypot(1, tau)));
  return tau * Math.hypot(1, sigma) - sigma * Math.hypot(1, tau);
}

// Newton iteration for the inverse of tauPrime; converges in 2 to 3 steps.
function tauFromTauPrime(tp) {
  let tau = tp;
  for (let i = 0; i < 6; i++) {
    const tpi = tauPrime(tau);
    const dtau = ((tp - tpi) / Math.hypot(1, tpi)) *
      ((1 + (1 - E2) * tau * tau) / ((1 - E2) * Math.hypot(1, tau)));
    tau += dtau;
    if (Math.abs(dtau) < 1e-14) break;
  }
  return tau;
}

// Gauss-Schreiber coordinates (xi', eta') for a latitude and a longitude offset.
function sphericalTM(lat, dlon) {
  const tp = tauPrime(Math.tan(lat));
  return {
    tp,
    xiP: Math.atan2(tp, Math.cos(dlon)),
    etaP: Math.asinh(Math.sin(dlon) / Math.hypot(tp, Math.cos(dlon))),
  };
}

function krugerForward(xiP, etaP) {
  let xi = xiP;
  let eta = etaP;
  let p = 1;
  let q = 0;
  for (let j = 1; j <= 6; j++) {
    const a = ALPHA[j - 1];
    const s = Math.sin(2 * j * xiP);
    const c = Math.cos(2 * j * xiP);
    const sh = Math.sinh(2 * j * etaP);
    const ch = Math.cosh(2 * j * etaP);
    xi += a * s * ch;
    eta += a * c * sh;
    p += 2 * j * a * c * ch;
    q += 2 * j * a * s * sh;
  }
  return { xi, eta, p, q };
}

const XI0 = krugerForward(sphericalTM(LAT0, 0).xiP, 0).xi;

/**
 * Geodetic latitude and longitude (degrees, NAD83(2011), treated as WGS84) to
 * EPSG:6527 easting and northing in metres (not feet).
 */
export function projectMetres(lat, lon) {
  const dlon = lon * DEG - LON0;
  const { xiP, etaP } = sphericalTM(lat * DEG, dlon);
  const { xi, eta } = krugerForward(xiP, etaP);
  return {
    e: FALSE_E + K0 * RECT_A * eta,
    n: FALSE_N + K0 * RECT_A * (xi - XI0),
  };
}

/** EPSG:6527 easting and northing in metres back to latitude and longitude in degrees. */
export function unprojectMetres(e, n) {
  const xi = (n - FALSE_N) / (K0 * RECT_A) + XI0;
  const eta = (e - FALSE_E) / (K0 * RECT_A);
  let xiP = xi;
  let etaP = eta;
  for (let j = 1; j <= 6; j++) {
    const b = BETA[j - 1];
    xiP -= b * Math.sin(2 * j * xi) * Math.cosh(2 * j * eta);
    etaP -= b * Math.cos(2 * j * xi) * Math.sinh(2 * j * eta);
  }
  const tp = Math.sin(xiP) / Math.hypot(Math.sinh(etaP), Math.cos(xiP));
  const dlon = Math.atan2(Math.sinh(etaP), Math.cos(xiP));
  return { lat: Math.atan(tauFromTauPrime(tp)) / DEG, lon: (LON0 + dlon) / DEG };
}

/** Latitude and longitude (degrees) to EPSG:6527 easting and northing in US survey feet. */
export function latLonToGrid(lat, lon) {
  const { e, n } = projectMetres(lat, lon);
  return { E: e / M_PER_FTUS, N: n / M_PER_FTUS };
}

/** EPSG:6527 easting and northing in US survey feet to latitude and longitude (degrees). */
export function gridToLatLon(E, N) {
  return unprojectMetres(E * M_PER_FTUS, N * M_PER_FTUS);
}

/** three.js metres (x east, z = -grid north) to latitude and longitude in degrees. */
export function localToLatLon(x, z) {
  return unprojectMetres(x + ORIGIN.E0 * M_PER_FTUS, -z + ORIGIN.N0 * M_PER_FTUS);
}

/** Latitude and longitude in degrees to three.js metres (x east, z = -grid north). */
export function latLonToLocal(lat, lon) {
  const { e, n } = projectMetres(lat, lon);
  return { x: e - ORIGIN.E0 * M_PER_FTUS, z: -(n - ORIGIN.N0 * M_PER_FTUS) };
}

/**
 * Grid convergence in degrees: the angle from true north to grid north,
 * positive when grid north is east of true north (east of the central meridian here).
 */
export function convergenceDeg(lat, lon) {
  const dlon = lon * DEG - LON0;
  const { tp, xiP, etaP } = sphericalTM(lat * DEG, dlon);
  const { p, q } = krugerForward(xiP, etaP);
  const gammaSphere = Math.atan((tp / Math.hypot(1, tp)) * Math.tan(dlon));
  return (gammaSphere + Math.atan2(q, p)) / DEG;
}

function wrap360(deg) {
  const r = deg % 360;
  return r < 0 ? r + 360 : r;
}

/** Bearing clockwise from grid north to bearing clockwise from true north, degrees in [0, 360). */
export function gridToTrueBearing(deg, lat, lon) {
  return wrap360(deg + convergenceDeg(lat, lon));
}

/** Bearing clockwise from true north to bearing clockwise from grid north, degrees in [0, 360). */
export function trueToGridBearing(deg, lat, lon) {
  return wrap360(deg - convergenceDeg(lat, lon));
}

/** Latitude and longitude (degrees) of the model's local origin, derived from ORIGIN. */
export const CAMPUS = Object.freeze(localToLatLon(0, 0));

/** Degrees to text such as `40.86000° N, 74.19720° W` (5 decimals, about 1 m). */
export function formatLatLon(lat, lon) {
  const ns = lat >= 0 ? 'N' : 'S';
  const ew = lon >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(5)}° ${ns}, ${Math.abs(lon).toFixed(5)}° ${ew}`;
}

/** Metres to text in metric and imperial, such as `12.4 m · 40.7 ft` or `1.25 km · 0.78 mi`. */
export function formatDistance(m) {
  if (Math.abs(m) >= 1000) {
    return `${(m / 1000).toFixed(2)} km · ${(m / 1609.344).toFixed(2)} mi`;
  }
  return `${m.toFixed(1)} m · ${(m / 0.3048).toFixed(1)} ft`;
}

const POINTS = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];

/** Bearing in degrees (any range) to the nearest of the 16 compass points. */
export function compassPoint(deg) {
  return POINTS[Math.round(wrap360(deg) / 22.5) % 16];
}
