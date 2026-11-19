import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  ORIGIN, M_PER_FTUS, CAMPUS,
  localToLatLon, latLonToLocal, latLonToGrid, gridToLatLon,
  convergenceDeg, gridToTrueBearing, trueToGridBearing,
  formatLatLon, formatDistance, compassPoint,
} from '../viewer/geo.js';

// Reference values from pyproj 3.8 (PROJ), Transformer.from_crs('EPSG:4326', 'EPSG:6527',
// always_xy=True), and Proj('EPSG:6527').get_factors(...).meridian_convergence.
const PYPROJ = [
  { lat: 40.8576232, lon: -74.2025840, E: 574390.0186700212, N: 737467.0794282184, conv: 0.19456508434860573 },
  { lat: 40.86, lon: -74.1972, E: 575876.2369432008, N: 738338.0617537225, conv: 0.1980967541693527 },
  { lat: 40.865, lon: -74.198, E: 575648.6836950618, N: 740158.8224850142, conv: 0.197593306713134 },
];

const near = (actual, expected, tol, msg) =>
  assert.ok(Math.abs(actual - expected) <= tol, `${msg}: ${actual} vs ${expected} (tol ${tol})`);

test('constants', () => {
  assert.equal(ORIGIN.E0, 575880);
  assert.equal(ORIGIN.N0, 738340);
  near(M_PER_FTUS, 0.3048006096, 1e-10, 'US survey foot');
});

test('forward projection matches pyproj within 1 mm', () => {
  for (const p of PYPROJ) {
    const g = latLonToGrid(p.lat, p.lon);
    near((g.E - p.E) * M_PER_FTUS, 0, 0.001, `E at ${p.lat},${p.lon}`);
    near((g.N - p.N) * M_PER_FTUS, 0, 0.001, `N at ${p.lat},${p.lon}`);
  }
});

test('inverse projection matches pyproj within 1 mm', () => {
  for (const p of PYPROJ) {
    const ll = gridToLatLon(p.E, p.N);
    near(ll.lat, p.lat, 1e-8, 'lat');
    near(ll.lon, p.lon, 1e-8, 'lon');
  }
});

test('convergence matches pyproj and is about 0.2 degrees east', () => {
  for (const p of PYPROJ) near(convergenceDeg(p.lat, p.lon), p.conv, 1e-6, 'convergence');
  // Numerical check: grid bearing of a short step due true north equals -convergence.
  const a = latLonToLocal(40.86, -74.2);
  const b = latLonToLocal(40.8601, -74.2);
  const gridBearing = Math.atan2(b.x - a.x, -(b.z - a.z)) * 180 / Math.PI;
  near(gridBearing, -convergenceDeg(40.86005, -74.2), 1e-4, 'numerical convergence');
});

test('Montclair Heights station (OSM node 7009814496) lands on the model', () => {
  const p = latLonToLocal(40.8576232, -74.2025840);
  near(p.x, -454.1, 0.2, 'x');
  near(p.z, 266.1, 0.2, 'z');
});

test('CAMPUS is the local origin', () => {
  near(CAMPUS.lat, 40.86000528461985, 1e-9, 'lat');
  near(CAMPUS.lon, -74.19718637073655, 1e-9, 'lon');
  const o = latLonToLocal(CAMPUS.lat, CAMPUS.lon);
  near(o.x, 0, 1e-6, 'x');
  near(o.z, 0, 1e-6, 'z');
});

test('local <-> lat/lon round trip within 1 mm over 5 km', () => {
  for (let x = -5000; x <= 5000; x += 1250) {
    for (let z = -5000; z <= 5000; z += 1250) {
      const ll = localToLatLon(x, z);
      const back = latLonToLocal(ll.lat, ll.lon);
      near(back.x, x, 0.001, 'x');
      near(back.z, z, 0.001, 'z');
    }
  }
});

test('-z is grid north', () => {
  const a = localToLatLon(0, 0);
  const b = localToLatLon(0, -100);
  assert.ok(b.lat > a.lat);
});

test('bearings convert both ways and wrap into [0, 360)', () => {
  const { lat, lon } = CAMPUS;
  const c = convergenceDeg(lat, lon);
  near(gridToTrueBearing(0, lat, lon), c, 1e-12, 'grid north');
  near(trueToGridBearing(0, lat, lon), 360 - c, 1e-9, 'true north wraps');
  near(trueToGridBearing(gridToTrueBearing(123.4, lat, lon), lat, lon), 123.4, 1e-9, 'round trip');
  near(gridToTrueBearing(359.9, lat, lon), 359.9 + c - 360, 1e-9, 'wrap past 360');
  assert.ok(gridToTrueBearing(-720, lat, lon) >= 0);
});

test('formatLatLon', () => {
  assert.equal(formatLatLon(40.86, -74.1972), '40.86000° N, 74.19720° W');
  assert.equal(formatLatLon(-33.5, 151.25), '33.50000° S, 151.25000° E');
});

test('formatDistance', () => {
  assert.equal(formatDistance(12.4), '12.4 m · 40.7 ft');
  assert.equal(formatDistance(0), '0.0 m · 0.0 ft');
  assert.equal(formatDistance(1609.344), '1.61 km · 1.00 mi');
});

test('compassPoint', () => {
  assert.equal(compassPoint(0), 'N');
  assert.equal(compassPoint(11), 'N');
  assert.equal(compassPoint(12), 'NNE');
  assert.equal(compassPoint(45), 'NE');
  assert.equal(compassPoint(180), 'S');
  assert.equal(compassPoint(292.5), 'WNW');
  assert.equal(compassPoint(355), 'N');
  assert.equal(compassPoint(-90), 'W');
  assert.equal(compassPoint(720 + 90), 'E');
});
