// Pure helpers for place labels and the guided tour: priority, decluttering, fading, stop selection
// and caption text. No DOM and no three, so node --test can run them.

/** How much a kind of place matters when labels compete for room. */
export const KIND_WEIGHT = { building: 4, station: 4, landmark: 4, sports: 2, parking: 1 };

/** Stops of the guided tour, in visiting order. Names match viewer/places.json. */
export const TOUR_NAMES = [
  'Red Hawk Deck', 'Alexander Kasser Theater', 'Susan A. Cole Hall', 'School of Communication and Media',
  'Life Hall', 'Memorial Auditorium', 'Schmitt Hall', 'Dickson Hall', 'Feliciano School of Business',
  'Student Center', 'University Hall', 'Center for Environmental and Life Sciences', 'Blanton Hall',
  'Montclair State University Ice Arena', 'NJ Transit Deck',
];

const KIND_TEXT = { building: 'Building', parking: 'Parking', sports: 'Sports', station: 'Station', landmark: 'Landmark' };

/**
 * Label priority: kind weight x footprint size x nearness. Bigger is more important.
 * The square root keeps a huge lot from beating a nearby hall on size alone.
 */
export function labelPriority(kind, r, distance) {
  const w = KIND_WEIGHT[kind] ?? 1;
  const size = Math.sqrt(Math.max(4, Number.isFinite(r) ? r : 0));
  const near = 1 / (1 + Math.max(0, distance) / 250);
  return w * size * near;
}

/**
 * Opacity for a label `distance` metres from the camera: full up to `near`, none beyond `far`.
 */
export function distanceOpacity(distance, near = 800, far = 1400) {
  if (!(distance < far)) return 0;
  if (distance <= near) return 1;
  return 1 - (distance - near) / (far - near);
}

/** Whether a place of `kind` may show at `distance` metres. Parking only shows close up. */
export function inRange(kind, distance, { far = 1400, parking = 350, minimum = 0 } = {}) {
  if (!(distance >= minimum)) return false;
  return distance <= (kind === 'parking' ? parking : far);
}

function overlaps(a, b, pad) {
  return a.x < b.x + b.w + pad && b.x < a.x + a.w + pad && a.y < b.y + b.h + pad && b.y < a.y + a.h + pad;
}

/**
 * Greedy declutter. `items` are { x, y, w, h, priority, forced } boxes in screen pixels (x, y top left).
 * Forced items go first and always show; the rest are taken by priority, skipping any that would
 * overlap one already placed, until `max` are shown. Returns the indices shown, in placing order.
 */
export function declutter(items, { max = Infinity, pad = 2 } = {}) {
  const order = items.map((_, i) => i).sort((a, b) => (items[b].forced ? 1 : 0) - (items[a].forced ? 1 : 0)
    || items[b].priority - items[a].priority);
  const placed = [];
  for (const i of order) {
    const it = items[i];
    if (!it.forced && placed.length >= max) break;
    if (!it.forced && placed.some(j => overlaps(items[j], it, pad))) continue;
    placed.push(i);
  }
  return placed;
}

/** Tour stops: the places named in `names`, in that order, skipping names that are missing. */
export function selectStops(places, names = TOUR_NAMES) {
  if (!Array.isArray(places)) return [];
  const byName = new Map();
  for (const p of places) if (p && typeof p.name === 'string' && !byName.has(p.name)) byName.set(p.name, p);
  return names.map(n => byName.get(n)).filter(Boolean);
}

/**
 * Caption text for a tour stop. Only facts from OpenStreetMap: the name, the kind and, when tagged,
 * start_date (which may be a construction date, so it is quoted as the tag, not as an opening year).
 */
export function tourCaption(place, index, count) {
  const details = [];
  if (KIND_TEXT[place?.kind]) details.push(KIND_TEXT[place.kind]);
  const start = place?.tags?.start_date;
  if (typeof start === 'string' && start.trim()) details.push(`OpenStreetMap start date: ${start.trim()}`);
  return { title: place?.name ?? '', counter: `${index + 1} of ${count}`, details, source: 'Names from OpenStreetMap' };
}

/** The tooltip that says where a label's name comes from. */
export function sourceTitle(place) {
  return place?.osm ? `Name and position from OpenStreetMap (${place.osm})` : 'Name and position from OpenStreetMap';
}

/**
 * Camera offset for a tour stop, framed like app.goToPlace but looking from the south-west.
 * Returns { dx, dy, dz } to add to the target. Viewer axes: +x east, -z grid north, so south-west is (-x, +z).
 */
export function southWestOffset(r) {
  const dist = Math.max(70, (r || 20) * 2.4);
  const h = dist * 0.8 / Math.SQRT2;
  return { dx: -h, dy: dist * 0.6, dz: h };
}
