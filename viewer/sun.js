// Solar position and sun times from the NOAA solar calculator equations (after Meeus,
// Astronomical Algorithms). Pure, no imports. Time is UT; Delta T (about 70 s) is
// ignored, which costs under 0.01 degrees.

const DEG = Math.PI / 180;
const MS_PER_DAY = 86400000;
const UNIX_EPOCH_JD = 2440587.5;

const sinD = (d) => Math.sin(d * DEG);
const cosD = (d) => Math.cos(d * DEG);

/** Julian day (UT) of a JS Date. */
export function julianDay(date) {
  return date.getTime() / MS_PER_DAY + UNIX_EPOCH_JD;
}

/** Julian centuries since J2000.0 for a JS Date. */
export function julianCentury(date) {
  return (julianDay(date) - 2451545) / 36525;
}

/**
 * Sun's declination (degrees) and the equation of time (minutes) at Julian century t.
 * Exported for tests and for anyone who wants the intermediate values.
 */
export function solarCoordinates(t) {
  const l0 = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360;
  const m = 357.52911 + t * (35999.05029 - 0.0001537 * t);
  const e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t);
  const c = sinD(m) * (1.914602 - t * (0.004817 + 0.000014 * t)) +
    sinD(2 * m) * (0.019993 - 0.000101 * t) +
    sinD(3 * m) * 0.000289;
  const omega = 125.04 - 1934.136 * t;
  const lambda = l0 + c - 0.00569 - 0.00478 * sinD(omega);
  const eps0 = 23 + (26 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60) / 60;
  const eps = eps0 + 0.00256 * cosD(omega);
  const declination = Math.asin(sinD(eps) * sinD(lambda)) / DEG;
  const y = Math.tan((eps / 2) * DEG) ** 2;
  const eqTime = 4 / DEG * (
    y * sinD(2 * l0) -
    2 * e * sinD(m) +
    4 * e * y * sinD(m) * cosD(2 * l0) -
    0.5 * y * y * sinD(4 * l0) -
    1.25 * e * e * sinD(2 * m)
  );
  return { declination, eqTime };
}

// NOAA's piecewise fit to standard refraction (degrees) for a geometric elevation.
function refraction(elev) {
  if (elev > 85) return 0;
  const te = Math.tan(elev * DEG);
  let arcsec;
  if (elev > 5) {
    arcsec = 58.1 / te - 0.07 / te ** 3 + 0.000086 / te ** 5;
  } else if (elev > -0.575) {
    arcsec = 1735 + elev * (-518.2 + elev * (103.4 + elev * (-12.79 + elev * 0.711)));
  } else {
    arcsec = -20.774 / te;
  }
  return arcsec / 3600;
}

/**
 * Sun position for an instant and a place.
 * @param {Date} date instant
 * @param {number} lat degrees north
 * @param {number} lon degrees east (negative west)
 * @returns {{ azimuth: number, elevation: number, apparent: number }} degrees; azimuth
 *   clockwise from true north in [0, 360), elevation geometric (sun's centre), apparent
 *   with refraction.
 */
export function sunPosition(date, lat, lon) {
  const { declination, eqTime } = solarCoordinates(julianCentury(date));
  const utcMinutes = (((date.getTime() % MS_PER_DAY) + MS_PER_DAY) % MS_PER_DAY) / 60000;
  const trueSolar = (((utcMinutes + eqTime + 4 * lon) % 1440) + 1440) % 1440;
  const hourAngle = trueSolar / 4 - 180;
  const cosZenith = Math.min(1, Math.max(-1,
    sinD(lat) * sinD(declination) + cosD(lat) * cosD(declination) * cosD(hourAngle)));
  const zenith = Math.acos(cosZenith) / DEG;
  const elevation = 90 - zenith;
  const az = Math.atan2(
    sinD(hourAngle),
    cosD(hourAngle) * sinD(lat) - Math.tan(declination * DEG) * cosD(lat),
  ) / DEG + 180;
  return { azimuth: az % 360, elevation, apparent: elevation + refraction(elevation) };
}

const formatters = new Map();

function formatterFor(timeZone) {
  let f = formatters.get(timeZone);
  if (!f) {
    f = new Intl.DateTimeFormat('en-US', {
      timeZone, hourCycle: 'h23',
      year: 'numeric', month: 'numeric', day: 'numeric',
      hour: 'numeric', minute: 'numeric', second: 'numeric',
    });
    formatters.set(timeZone, f);
  }
  return f;
}

/**
 * Wall-clock parts of an instant in a time zone.
 * @returns {{ year: number, month: number, day: number, hour: number, minute: number,
 *   second: number }} month 1 to 12, hour 0 to 23
 */
export function zonedParts(date, timeZone = 'America/New_York') {
  const out = {};
  for (const { type, value } of formatterFor(timeZone).formatToParts(date)) {
    if (type !== 'literal') out[type] = Number(value);
  }
  return {
    year: out.year, month: out.month, day: out.day,
    hour: out.hour % 24, minute: out.minute, second: out.second,
  };
}

// Offset of the zone from UTC at an instant, in milliseconds (EDT is -4 h).
function offsetAt(ms, timeZone) {
  const p = zonedParts(new Date(ms), timeZone);
  const wall = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute, p.second);
  return wall - Math.floor(ms / 1000) * 1000;
}

/**
 * The instant at which a wall clock in a time zone shows the given time.
 * Ambiguous times (the repeated hour in November) resolve to the earlier instant;
 * times skipped in March resolve forward by the gap (2:30 becomes 3:30 daylight time),
 * as Temporal's 'compatible' option does.
 * @param {{ year: number, month: number, day: number, hour?: number, minute?: number,
 *   second?: number }} parts month 1 to 12
 * @returns {Date}
 */
export function zonedDate(parts, timeZone = 'America/New_York') {
  const { year, month, day, hour = 0, minute = 0, second = 0 } = parts;
  const wall = Date.UTC(year, month - 1, day, hour, minute, second);
  const before = offsetAt(wall - MS_PER_DAY, timeZone);
  const after = offsetAt(wall + MS_PER_DAY, timeZone);
  const matches = [...new Set([before, after])]
    .map((offset) => wall - offset)
    .filter((ms) => offsetAt(ms, timeZone) === wall - ms)
    .sort((a, b) => a - b);
  return new Date(matches.length ? matches[0] : wall - before);
}

/** Day of the year (1 to 366) of a calendar date; month 1 to 12. */
export function dayOfYear(year, month, day) {
  return Math.round((Date.UTC(year, month - 1, day) - Date.UTC(year, 0, 1)) / MS_PER_DAY) + 1;
}

// Minutes after 00:00 UTC of the calendar date at which the event happens; NOAA's
// iterative method, evaluated at the event's own time for accuracy.
function eventMinutes(dayStartMs, lat, lon, kind) {
  let minutes = 720 - 4 * lon;
  for (let i = 0; i < 3; i++) {
    const t = julianCentury(new Date(dayStartMs + minutes * 60000));
    const { declination, eqTime } = solarCoordinates(t);
    if (kind === 'noon') {
      minutes = 720 - 4 * lon - eqTime;
      continue;
    }
    // 90.833 degrees: refraction at the horizon plus the sun's semidiameter.
    const cosHa = cosD(90.833) / (cosD(lat) * cosD(declination)) -
      Math.tan(lat * DEG) * Math.tan(declination * DEG);
    if (cosHa > 1 || cosHa < -1) return null;
    const ha = Math.acos(cosHa) / DEG;
    minutes = 720 - 4 * (lon + (kind === 'rise' ? ha : -ha)) - eqTime;
  }
  return minutes;
}

/**
 * Sunrise, solar noon and sunset for the local calendar day containing `date`.
 * @param {Date} date any instant on the day wanted
 * @param {number} lat degrees north
 * @param {number} lon degrees east (negative west)
 * @param {{ timeZone?: string }} [options] zone that defines the calendar day
 * @returns {{ sunrise: Date|null, solarNoon: Date, sunset: Date|null }} null for sunrise
 *   and sunset in polar day or night
 */
export function sunTimes(date, lat, lon, { timeZone = 'America/New_York' } = {}) {
  const { year, month, day } = zonedParts(date, timeZone);
  const dayStart = Date.UTC(year, month - 1, day);
  const at = (kind) => {
    const m = eventMinutes(dayStart, lat, lon, kind);
    return m === null ? null : new Date(dayStart + Math.round(m * 60000));
  };
  return { sunrise: at('rise'), solarNoon: at('noon'), sunset: at('set') };
}
