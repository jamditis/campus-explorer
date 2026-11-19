// Search and nearest-place lookups over places.json. Pure: no imports, no DOM.
// Place x and z are three.js viewer metres (x east, -z grid north); r is the footprint radius in metres.

// Lower level = better match. Alternate names sit just below every name level, and the
// typo-tolerant subsequence match comes last.
const NAME_LEVELS = 5;
const SUBSEQUENCE_LEVEL = NAME_LEVELS * 2;
const MAX_SCORE = SUBSEQUENCE_LEVEL + 1;

/**
 * Fold text for matching: lower case, diacritics removed, apostrophes dropped, other
 * punctuation turned into spaces, whitespace collapsed.
 */
export function normalize(text) {
  if (typeof text !== 'string') return '';
  return text
    .normalize('NFKD')
    .replace(/\p{M}/gu, '')
    .toLowerCase()
    // "O'Neil" should match "oneil", so apostrophes join rather than split.
    .replace(/['‘’ʼ`]/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}


function isSubsequence(needle, hay) {
  let i = 0;
  for (let j = 0; j < hay.length && i < needle.length; j++) {
    if (hay[j] === needle[i]) i++;
  }
  return i === needle.length;
}

// Level 0..4 for a folded candidate against a folded query, or -1.
function matchLevel(text, query, queryWords) {
  if (!text) return -1;
  if (text === query) return 0;
  if (text.startsWith(query)) return 1;
  if (text.includes(` ${query}`)) return 2;
  const words = text.split(' ');
  if (queryWords.every((q) => words.some((w) => w.startsWith(q)))) return 3;
  if (text.includes(query)) return 4;
  return -1;
}

function altNames(place) {
  const tags = place.tags && typeof place.tags === 'object' ? place.tags : {};
  const out = [];
  for (const key of ['alt_name', 'short_name']) {
    // OSM separates several values with ';'.
    if (typeof tags[key] === 'string') out.push(...tags[key].split(';'));
  }
  return out.map(normalize).filter(Boolean);
}

function bestLevel(candidates, query, queryWords) {
  let best = -1;
  for (const c of candidates) {
    const level = matchLevel(c, query, queryWords);
    if (level >= 0 && (best < 0 || level < best)) best = level;
  }
  return best;
}

function placeLevel(place, query, queryWords) {
  const name = normalize(place.name);
  const alts = altNames(place);
  const nameLevel = matchLevel(name, query, queryWords);
  if (nameLevel >= 0) return nameLevel;
  const altLevel = bestLevel(alts, query, queryWords);
  if (altLevel >= 0) return NAME_LEVELS + altLevel;
  const compact = query.replace(/ /g, '');
  if (compact.length >= 3 && [name, ...alts].some((c) => isSubsequence(compact, c.replace(/ /g, '')))) {
    return SUBSEQUENCE_LEVEL;
  }
  return -1;
}

/**
 * Rank places for a search query. Returns up to `limit` { place, score }, best first;
 * score is higher for better matches (11 exact name down to 1 subsequence). Ties go to the
 * shorter name, then alphabetical. Empty or whitespace query returns [].
 */
export function searchPlaces(places, query, limit = 8) {
  if (!Array.isArray(places)) return [];
  const q = normalize(query);
  if (!q) return [];
  const queryWords = q.split(' ');
  const hits = [];
  for (const place of places) {
    if (!place || typeof place.name !== 'string') continue;
    const level = placeLevel(place, q, queryWords);
    if (level >= 0) hits.push({ place, score: MAX_SCORE - level });
  }
  hits.sort((a, b) => b.score - a.score
    || a.place.name.length - b.place.name.length
    || (a.place.name < b.place.name ? -1 : a.place.name > b.place.name ? 1 : 0));
  const n = Number.isFinite(limit) ? Math.max(0, Math.floor(limit)) : hits.length;
  return hits.slice(0, n);
}

/**
 * The place whose footprint circle is nearest to (x, z) in viewer metres, within
 * maxDistance metres. distance = max(0, hypot(dx, dz) - r). Returns null when none qualify.
 */
export function nearestPlace(places, x, z, maxDistance = Infinity) {
  if (!Array.isArray(places) || !Number.isFinite(x) || !Number.isFinite(z)) return null;
  let best = null;
  for (const place of places) {
    if (!place || !Number.isFinite(place.x) || !Number.isFinite(place.z)) continue;
    const r = Number.isFinite(place.r) && place.r > 0 ? place.r : 0;
    const distance = Math.max(0, Math.hypot(place.x - x, place.z - z) - r);
    if (distance > maxDistance) continue;
    if (!best || distance < best.distance) best = { place, distance };
  }
  return best;
}
