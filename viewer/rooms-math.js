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
    volumes.push({ id: String(v.id ?? ''), building: String(v.building ?? ''), short: String(v.short ?? ''), ring: v.ring.map(p => [p[0], p[1]]), y0: v.y0, y1: v.y1, ceiling: num(v.ceiling) ? v.ceiling : v.y1, levels });
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
  return inRing(ring, x, z) ? 0 : edgeGap(ring, x, z);
}

/** Horizontal distance from (x, z) to the nearest edge of the ring, inside or out. */
export function edgeGap(ring, x, z) {
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

/** Fragments nearer than this (metres) to the outline are the shell's outer face: no interior light. */
export const EDGE = 0.2;
/** Room points nearer than this (metres) to the camera, on its floor, mark the room it stands in. */
export const ROOM_HERE = 5;

/**
 * Does the point (with world normal y `ny`) take the interior light (look.js, same rule in GLSL)? Inside
 * the outline and more than EDGE from it, from just below the lowest floor to the top of the shell (in its
 * top half metre only surfaces facing down: the roof's underside, not the parapets), and not a surface
 * facing up above the interior ceiling (the roof).
 */
export function interiorLit(v, x, y, z, ny) {
  if (y < v.y0 - 0.3 || y > v.y1) return false;
  if (y > v.y1 - 0.5 && ny > -0.5) return false; // the top half metre: parapets, but the roof's underside is lit
  if (ny > 0.5 && y > v.ceiling + 0.5) return false;
  return inRing(v.ring, x, z) && edgeGap(v.ring, x, z) > EDGE;
}

/** Share of the interior light a surface takes by its world normal y: ceilings all, walls 0.8, floors 0.55. */
export function ambientFactor(ny) {
  return ny < -0.5 ? 1 : ny > 0.5 ? 0.55 : 0.8;
}

/** Index of the room the camera stands in: the nearest room point on its floor within ROOM_HERE, inside the building; else -1. */
export function roomHere(data, cam) {
  let best = -1, bd = ROOM_HERE;
  for (const v of data.volumes) {
    if (!inVolume(v, cam.x, cam.y, cam.z)) continue;
    const f = floorAt(v.levels, cam.y);
    data.rooms.forEach((r, i) => {
      if (r.building !== v.building || r.floor !== f) return;
      const d = Math.hypot(r.x - cam.x, r.z - cam.z);
      if (d <= bd) { bd = d; best = i; }
    });
  }
  return best;
}

/**
 * Room labels by line of sight. `ids`: the rooms that may show; `memo`: Map id -> { clear, pass } kept between
 * passes; `cast(id)`: true when nothing solid lies between the camera and that room's label point. Casts at most
 * `budget` rays, rooms never checked first, then the longest unchecked; returns the Set of rooms to show: those
 * last seen clear, and always `here`, the room the camera stands in.
 */
export function sightPass(ids, memo, cast, { budget = 12, here = -1 } = {}) {
  const pass = (memo.pass = (memo.pass ?? 0) + 1);
  const order = ids.filter(id => id !== here).sort((a, b) => (memo.get(a)?.pass ?? -1) - (memo.get(b)?.pass ?? -1));
  for (const id of order.slice(0, budget)) memo.set(id, { clear: !!cast(id), pass });
  const shown = new Set(ids.filter(id => memo.get(id)?.clear));
  if (here >= 0) shown.add(here);
  return shown;
}

/** True while a room that may show still waits for its ray since pass `from`. The room the camera stands in
 * never gets a ray (sightPass), so it never counts: else the label pass would not settle while you stand in a room. */
export function sightPending(ids, memo, from, here = -1) {
  return ids.some(id => id !== here && (memo.get(id)?.pass ?? 0) < from);
}

/** Texels per row of the volume texture (packVolumes); also the most volumes it holds. */
export const VOL_TEX_W = 256;

/**
 * Every volume packed for the shaders (look.js), as RGBA float texels in rows of VOL_TEX_W, so the count is limited
 * only by the texture (256 volumes, any number of ring points), not by shader uniform slots. Texel index i lies at
 * (i % W, floor(i / W)). Texel v: ring start, ring length, y0, y1. Texel W + v: the ring's box grown by `grow`
 * (x0, z0, x1, z1). Texel 2W + v: ceiling. Texel 3W + k: ring point k (x, z). Returns { data, width, height, n }.
 */
export function packVolumes(volumes, grow = GLASS_GROW, W = VOL_TEX_W) {
  const vs = volumes.slice(0, W), points = vs.reduce((s, v) => s + v.ring.length, 0);
  const height = 3 + Math.max(1, Math.ceil(points / W)), data = new Float32Array(W * height * 4);
  const put = (i, a, b, c, d) => data.set([a, b, c, d], i * 4);
  let at = 0;
  vs.forEach((v, k) => {
    const xs = v.ring.map(p => p[0]), zs = v.ring.map(p => p[1]);
    put(k, at, v.ring.length, v.y0, v.y1);
    put(W + k, Math.min(...xs) - grow, Math.min(...zs) - grow, Math.max(...xs) + grow, Math.max(...zs) + grow);
    put(2 * W + k, v.ceiling ?? v.y1, 0, 0, 0);
    v.ring.forEach((p, j) => put(3 * W + at + j, p[0], p[1], 0, 0));
    at += v.ring.length;
  });
  return { data, width: W, height, n: vs.length };
}
