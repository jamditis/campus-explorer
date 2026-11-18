// View state <-> URL hash. Pure: no imports, no DOM.
// Coordinates are three.js viewer metres: x east, y up, -z grid north.

const VERSION = 1;
const SCENES = ['main', 'north'];
const MODES = ['orbit', 'fly', 'walk'];
const COORD_LIMIT = 20000;
const COORD_PATTERN = /^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$/;
const TIME_PATTERN = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/;

function formatNumber(n) {
  const text = (Math.round(n * 10) / 10).toFixed(1);
  // Rounding can leave "-0.0", which would make the hash differ for the same view.
  return text === '-0.0' ? '0.0' : text;
}

function isVector(v) {
  return Array.isArray(v) && v.length === 3 && v.every((n) => typeof n === 'number' && Number.isFinite(n));
}

function formatVector(v) {
  return v.map(formatNumber).join(',');
}

function parseVector(text) {
  const parts = text.split(',');
  if (parts.length !== 3) return undefined;
  const out = [];
  for (const part of parts) {
    const trimmed = part.trim();
    // Number('') is 0 and Number('0x10') is 16; only plain decimals are accepted.
    if (!COORD_PATTERN.test(trimmed)) return undefined;
    const n = Number(trimmed);
    if (!Number.isFinite(n) || Math.abs(n) > COORD_LIMIT) return undefined;
    out.push(Math.round(n * 10) / 10 + 0);
  }
  return out;
}

function daysInMonth(year, month) {
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  return [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1];
}

function parseTime(text) {
  const match = TIME_PATTERN.exec(text);
  if (!match) return undefined;
  const [year, month, day, hour, minute] = match.slice(1).map(Number);
  if (year < 1 || month < 1 || month > 12) return undefined;
  if (day < 1 || day > daysInMonth(year, month)) return undefined;
  if (hour > 23 || minute > 59) return undefined;
  return text;
}

function isTime(value) {
  return typeof value === 'string' && parseTime(value) !== undefined;
}

/**
 * Encode a view as a URL hash body (no leading '#').
 * position and target are three.js viewer metres (x east, y up, -z grid north), rounded to 0.1 m.
 * time is local wall-clock 'YYYY-MM-DDTHH:MM' or null. Invalid or missing fields are left out.
 * @param {{scene?: string, mode?: string, position?: number[], target?: number[], time?: string|null, labels?: boolean}} view
 * @returns {string}
 */
export function encodeView(view) {
  const v = view && typeof view === 'object' ? view : {};
  const parts = [`v=${VERSION}`];
  if (SCENES.includes(v.scene)) parts.push(`s=${v.scene}`);
  if (MODES.includes(v.mode)) parts.push(`m=${v.mode}`);
  if (isVector(v.position)) parts.push(`c=${formatVector(v.position)}`);
  if (isVector(v.target)) parts.push(`t=${formatVector(v.target)}`);
  if (isTime(v.time)) parts.push(`d=${v.time}`);
  if (v.labels === true) parts.push('l=1');
  return parts.join('&');
}

/**
 * Decode a URL hash (with or without '#') into a view. Never throws.
 * Unusable fields come back undefined so the caller keeps its default. An absent 'd' means
 * time null and an absent 'l' means labels false, matching what encodeView leaves out.
 * Coordinates are three.js viewer metres, each within +-20000.
 * @param {string} hash
 * @returns {{scene?: string, mode?: string, position?: number[], target?: number[], time?: string|null, labels: boolean} | null}
 *   null when no field was usable.
 */
export function decodeView(hash) {
  if (typeof hash !== 'string') return null;
  let params;
  try {
    params = new URLSearchParams(hash.replace(/^#/, ''));
  } catch {
    return null;
  }
  // A later 'v' may add fields; we still read the ones this version knows.
  const get = (key) => {
    const value = params.get(key);
    return value === null ? null : value.trim();
  };
  let usable = 0;
  const view = {
    scene: undefined,
    mode: undefined,
    position: undefined,
    target: undefined,
    time: null,
    labels: false,
  };

  const scene = get('s');
  if (scene !== null && SCENES.includes(scene)) { view.scene = scene; usable++; }
  const mode = get('m');
  if (mode !== null && MODES.includes(mode)) { view.mode = mode; usable++; }
  const c = get('c');
  if (c !== null) {
    view.position = parseVector(c);
    if (view.position) usable++;
  }
  const t = get('t');
  if (t !== null) {
    view.target = parseVector(t);
    if (view.target) usable++;
  }
  const d = get('d');
  if (d !== null) {
    view.time = parseTime(d);
    if (view.time) usable++;
  }
  const l = get('l');
  if (l === '1' || l === '0') { view.labels = l === '1'; usable++; }

  return usable > 0 ? view : null;
}
