// Pure. Buildings with a real interior (viewer/rooms.json, built by tools/places/build_rooms.py):
// their volumes, which floor the camera is on, which room labels show, and rooms as search places.
// No DOM and no three. Coordinates are viewer metres: x east, y up, -z grid north.

/** Within this many metres of a volume its interior is drawn whatever its screen size (look.js). */
export const INTERIOR_REACH = 40;
/** Room labels show within this many metres. */
export const ROOM_REACH = 20;
/** Glass this close to a volume (metres) belongs to its building and is drawn see-through. */
export const GLASS_GROW = 1;

const num = Number.isFinite;
const point = p => Array.isArray(p) && p.length >= 2 && num(p[0]) && num(p[1]);

/** Check and normalise rooms.json. Broken volumes and rooms are dropped; levels sorted bottom up. */
export function parseRooms(data) {
  const volumes = [], rooms = [];
  for (const v of Array.isArray(data?.volumes) ? data.volumes : []) {
    if (!v || !Array.isArray(v.ring) || v.ring.length < 3 || !v.ring.every(point) || !num(v.y0) || !num(v.y1)) continue;
    const levels = (Array.isArray(v.levels) ? v.levels : []).filter(l => l && num(l.floor) && num(l.y)).sort((a, b) => a.y - b.y);
    volumes.push({ id: String(v.id ?? ''), building: String(v.building ?? ''), short: String(v.short ?? ''), ring: v.ring.map(p => [p[0], p[1]]), y0: v.y0, y1: v.y1, levels });
  }
  for (const r of Array.isArray(data?.rooms) ? data.rooms : []) {
    if (!r || typeof r.name !== 'string' || !r.name || ![r.x, r.y, r.z, r.floor].every(num)) continue;
    rooms.push({ name: r.name, x: r.x, y: r.y, z: r.z, floor: r.floor, building: String(r.building ?? ''), unverified: r.unverified !== false });
  }
  return { volumes, rooms };
}

/** Is (x, z) inside the ring [[x, z], ...]? Even-odd rule. */
export function inRing(ring, x, z) {
  let hit = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [ax, az] = ring[i], [bx, bz] = ring[j];
    if ((az > z) !== (bz > z) && x < ax + (z - az) * (bx - ax) / (bz - az)) hit = !hit;
  }
  return hit;
}

/** Horizontal distance from (x, z) to the ring: 0 inside. */
export function ringGap(ring, x, z) {
  if (inRing(ring, x, z)) return 0;
  let best = Infinity;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [ax, az] = ring[j], [bx, bz] = ring[i], ux = bx - ax, uz = bz - az, l2 = ux * ux + uz * uz;
    const t = l2 ? Math.max(0, Math.min(1, ((x - ax) * ux + (z - az) * uz) / l2)) : 0;
    best = Math.min(best, Math.hypot(x - ax - ux * t, z - az - uz * t));
  }
  return best;
}

/** Is the point inside the volume grown by `grow` metres (sideways, up and down)? */
export function inVolume(v, x, y, z, grow = 0) {
  return y >= v.y0 - grow && y <= v.y1 + grow && ringGap(v.ring, x, z) <= grow;
}

/** Straight-line distance from the point to the volume: 0 inside. */
export function volumeGap(v, x, y, z) {
  return Math.hypot(ringGap(v.ring, x, z), Math.max(0, v.y0 - y, y - v.y1));
}

/** Indices of the volumes within `reach` metres of `p` ({x, y, z}). */
export function nearVolumes(volumes, p, reach = INTERIOR_REACH) {
  const out = [];
  volumes.forEach((v, i) => { if (volumeGap(v, p.x, p.y, p.z) <= reach) out.push(i); });
  return out;
}

/** Index of the volume `p` is inside, or -1. */
export function volumeAt(volumes, p) {
  return volumes.findIndex(v => inVolume(v, p.x, p.y, p.z));
}

/** Floor number for a camera at height `y`: the highest level at least half a metre below it. */
export function floorAt(levels, y) {
  if (!levels.length) return null;
  let f = levels[0].floor;
  for (const l of levels) if (l.y <= y - 0.5) f = l.floor;
  return f;
}

/**
 * Indices of the rooms whose labels show for a camera at `cam` in `mode`: only rooms on the floor the
 * camera is on (by its height against the room's building levels), within `reach` metres (level
 * distance), and only in walk mode or with the camera inside that building's volume.
 */
export function visibleRooms(data, cam, mode, { reach = ROOM_REACH } = {}) {
  const out = [], state = new Map();
  for (const v of data.volumes) {
    state.set(v.building, { floor: floorAt(v.levels, cam.y), ok: mode === 'walk' || inVolume(v, cam.x, cam.y, cam.z) });
  }
  data.rooms.forEach((r, i) => {
    const s = state.get(r.building);
    if (s && s.ok && s.floor === r.floor && Math.hypot(r.x - cam.x, r.z - cam.z) <= reach) out.push(i);
  });
  return out;
}

/** Rooms as places for search and app.goToPlace: "CCOM 2007", kind `room`, with their floor height. */
export function roomPlaces(data) {
  const short = new Map(data.volumes.map(v => [v.building, v.short || v.building]));
  return data.rooms.map(r => ({
    name: `${short.get(r.building) ?? r.building} ${r.name}`, kind: 'room', x: r.x, z: r.z, y: r.y, r: 3,
    floor: r.floor, building: r.building, unverified: r.unverified, tags: { alt_name: `Room ${r.name};${r.name}` },
  }));
}

/** What a search looks through: rooms join the places only when the query has a digit. */
export function searchPool(places, rooms, query) {
  return /\d/.test(query ?? '') ? places.concat(rooms) : places;
}

/** Height to start walking from when walk mode starts: the storey the camera is on (orbit, fly), else none. */
export function walkStartY(from, y) {
  return (from === 'orbit' || from === 'fly') && num(y) ? y : null;
}
