import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sunPosition, sunTimes, zonedDate, zonedParts, dayOfYear, julianDay } from '../viewer/sun.js';

const LAT = 40.86;
const LON = -74.1972;

const near = (actual, expected, tol, msg) =>
  assert.ok(Math.abs(actual - expected) <= tol, `${msg}: ${actual} vs ${expected} (tol ${tol})`);

// Reference values from PyEphem 4.2.1 (VSOP87, independent of the NOAA equations) at
// lat 40.86, lon -74.1972: [instant, azimuth, geometric elevation, apparent elevation]
// with pressure 0 for geometric and 1010 hPa, 10 C for apparent.
const EPHEM = [
  ['2026-01-03T14:17:00Z', 140.9759, 15.7982, 15.8550],
  ['2026-03-14T15:05:00Z', 139.8385, 38.7465, 38.7665],
  ['2026-05-22T15:53:00Z', 143.2436, 65.9019, 65.9091],
  ['2026-06-25T16:17:00Z', 149.7442, 70.3691, 70.3748],
  ['2026-07-13T04:29:00Z', 351.2732, -26.8339, null],
  ['2026-09-03T17:05:00Z', 184.0028, 56.4378, 56.4484],
  ['2026-10-25T05:41:00Z', 28.9023, -58.3687, null],
  ['2026-11-11T17:53:00Z', 199.7726, 29.2173, 29.2461],
  ['2026-12-15T18:17:00Z', 201.1723, 22.8775, 22.9157],
  ['2000-06-21T16:00:00Z', 140.3196, 68.6733, 68.6796],
  ['2099-12-21T17:00:00Z', 181.2847, 25.6986, 25.7321],
  ['2026-03-20T11:05:00Z', 90.1706, 0.1023, 0.5658],
];

function angleDiff(a, b) {
  const d = Math.abs(a - b) % 360;
  return Math.min(d, 360 - d);
}

test('sun position matches PyEphem within 0.1 degrees', () => {
  for (const [iso, az, el, app] of EPHEM) {
    const s = sunPosition(new Date(iso), LAT, LON);
    assert.ok(angleDiff(s.azimuth, az) <= 0.1, `azimuth ${iso}: ${s.azimuth} vs ${az}`);
    near(s.elevation, el, 0.1, `elevation ${iso}`);
    if (app !== null) near(s.apparent, app, el < 2 ? 0.3 : 0.1, `apparent ${iso}`);
    assert.ok(s.azimuth >= 0 && s.azimuth < 360);
  }
});

test('refraction lifts the sun and vanishes near the zenith', () => {
  const s = sunPosition(new Date('2026-03-20T11:05:00Z'), LAT, LON);
  assert.ok(s.apparent - s.elevation > 0.4 && s.apparent - s.elevation < 0.6);
  const high = sunPosition(new Date('2026-06-21T12:00:00Z'), 23.44, 0);
  assert.ok(high.apparent - high.elevation < 0.01);
});

// PyEphem rise and set of the sun's centre at -50 arcminutes, transit for noon.
const TIMES = [
  ['2026-01-15', '2026-01-15T12:19:03Z', '2026-01-15T17:06:15Z', '2026-01-15T21:53:45Z'],
  ['2026-03-08', '2026-03-08T11:19:43Z', '2026-03-08T17:07:28Z', '2026-03-08T22:55:52Z'],
  ['2026-06-21', '2026-06-21T09:25:18Z', '2026-06-21T16:58:39Z', '2026-06-22T00:32:00Z'],
  ['2026-11-01', '2026-11-01T11:27:29Z', '2026-11-01T16:40:22Z', '2026-11-01T21:52:44Z'],
  ['2026-12-21', '2026-12-21T12:17:49Z', '2026-12-21T16:54:57Z', '2026-12-21T21:32:06Z'],
];

test('sunrise, solar noon and sunset within 2 minutes of PyEphem', () => {
  for (const [day, rise, noon, set] of TIMES) {
    // Late evening local time, after 00:00 UTC, still selects the local calendar day.
    const [y, m, d] = day.split('-').map(Number);
    for (const hour of [0, 12, 23]) {
      const t = sunTimes(zonedDate({ year: y, month: m, day: d, hour, minute: 30 }), LAT, LON);
      near((t.sunrise - new Date(rise)) / 60000, 0, 2, `sunrise ${day}`);
      near((t.solarNoon - new Date(noon)) / 60000, 0, 2, `noon ${day}`);
      near((t.sunset - new Date(set)) / 60000, 0, 2, `sunset ${day}`);
    }
  }
});

test('polar day and night give null sunrise and sunset', () => {
  const midsummer = sunTimes(new Date('2026-06-21T12:00:00Z'), 78.2, 15.6, { timeZone: 'UTC' });
  assert.equal(midsummer.sunrise, null);
  assert.equal(midsummer.sunset, null);
  assert.ok(midsummer.solarNoon instanceof Date);
  const midwinter = sunTimes(new Date('2026-12-21T12:00:00Z'), 78.2, 15.6, { timeZone: 'UTC' });
  assert.equal(midwinter.sunrise, null);
});

test('zonedDate handles the March change (2026-03-08)', () => {
  const at = (hour, minute) => zonedDate({ year: 2026, month: 3, day: 8, hour, minute }).toISOString();
  assert.equal(at(1, 30), '2026-03-08T06:30:00.000Z');
  assert.equal(at(3, 30), '2026-03-08T07:30:00.000Z');
  // 02:30 does not exist; it moves forward by the gap, like Temporal's 'compatible'.
  assert.equal(at(2, 30), '2026-03-08T07:30:00.000Z');
  assert.equal(zonedDate({ year: 2026, month: 3, day: 7, hour: 12, minute: 0 }).toISOString(),
    '2026-03-07T17:00:00.000Z');
  assert.equal(zonedDate({ year: 2026, month: 3, day: 9, hour: 12, minute: 0 }).toISOString(),
    '2026-03-09T16:00:00.000Z');
});

test('zonedDate handles the November change (2026-11-01)', () => {
  const at = (hour, minute) => zonedDate({ year: 2026, month: 11, day: 1, hour, minute }).toISOString();
  assert.equal(at(0, 30), '2026-11-01T04:30:00.000Z');
  // 01:30 happens twice; the earlier (daylight time) instant wins.
  assert.equal(at(1, 30), '2026-11-01T05:30:00.000Z');
  assert.equal(at(2, 30), '2026-11-01T07:30:00.000Z');
  assert.equal(zonedDate({ year: 2026, month: 10, day: 31, hour: 12, minute: 0 }).toISOString(),
    '2026-10-31T16:00:00.000Z');
  assert.equal(zonedDate({ year: 2026, month: 11, day: 2, hour: 12, minute: 0 }).toISOString(),
    '2026-11-02T17:00:00.000Z');
});

test('zonedDate works in other zones', () => {
  assert.equal(zonedDate({ year: 2026, month: 7, day: 1, hour: 9, minute: 0 }, 'UTC').toISOString(),
    '2026-07-01T09:00:00.000Z');
  assert.equal(
    zonedDate({ year: 2026, month: 7, day: 1, hour: 9, minute: 0 }, 'Asia/Kolkata').toISOString(),
    '2026-07-01T03:30:00.000Z');
});

test('zonedParts is the inverse of zonedDate', () => {
  for (let h = 0; h < 24; h++) {
    const parts = { year: 2026, month: 6, day: 15, hour: h, minute: 7 };
    const p = zonedParts(zonedDate(parts));
    assert.deepEqual({ year: p.year, month: p.month, day: p.day, hour: p.hour, minute: p.minute }, parts);
  }
  const p = zonedParts(new Date('2026-11-01T06:30:00Z'));
  assert.equal(p.hour, 1);
  assert.equal(p.day, 1);
});

test('dayOfYear and julianDay', () => {
  assert.equal(dayOfYear(2026, 1, 1), 1);
  assert.equal(dayOfYear(2026, 12, 31), 365);
  assert.equal(dayOfYear(2024, 12, 31), 366);
  assert.equal(dayOfYear(2026, 3, 8), 67);
  assert.equal(julianDay(new Date('2000-01-01T12:00:00Z')), 2451545);
});
