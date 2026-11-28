// Pure routing for viewer/route.js: the walkable graph from viewer/paths.json and A* over it.
// No imports, so node --test can run it without three or a DOM.

export const STEPS = 1, STEEP = 2, STREET = 4, CROSSING = 8;
const STREET_COST = 1.25; // walking along a street counts a quarter longer than a footway
const SNAP_M = 120;       // farther than this from any path, there is no route

/** Graph from paths.json: { x, z (Float64Array), edges [{ a, b, flags, grade, length }], adj [[edge index]], entrances }. */
export function parsePaths(json) {
  const n = (json?.nodes?.length ?? 0) >> 1;
  const x = new Float64Array(n), z = new Float64Array(n);
  for (let i = 0; i < n; i++) { x[i] = json.nodes[2 * i]; z[i] = json.nodes[2 * i + 1]; }
  const adj = Array.from({ length: n }, () => []);
  const edges = (json?.edges ?? []).map(([a, b, flags, grade], i) => {
    adj[a].push(i); adj[b].push(i);
    return { a, b, flags, grade, length: Math.hypot(x[b] - x[a], z[b] - z[a]) };
  });
  const entrances = new Map();
  for (const e of json?.entrances ?? []) {
    if (!entrances.has(e.osm)) entrances.set(e.osm, []);
    entrances.get(e.osm).push({ node: e.node, mapped: !!e.mapped });
  }
  return { x, z, edges, adj, entrances, steepPct: json?.steep_pct ?? 8.33 };
}

const usable = (edge, stepFree) => !stepFree || !(edge.flags & (STEPS | STEEP));
const cost = edge => edge.length * (edge.flags & STREET ? STREET_COST : 1);

/**
 * The nearest point on a usable edge to (x, z): { edge, t, x, z, distance }, or null past `reach` metres.
 * `t` runs from the edge's a (0) to b (1).
 */
export function snap(g, x, z, { stepFree = false, reach = SNAP_M } = {}) {
  let best = null;
  g.edges.forEach((e, i) => {
    if (!usable(e, stepFree)) return;
    const ax = g.x[e.a], az = g.z[e.a], dx = g.x[e.b] - ax, dz = g.z[e.b] - az;
    const len2 = dx * dx + dz * dz;
    const t = len2 > 0 ? Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / len2)) : 0;
    const px = ax + t * dx, pz = az + t * dz, d = Math.hypot(x - px, z - pz);
    if (d <= reach && (!best || d < best.distance)) best = { edge: i, t, x: px, z: pz, distance: d };
  });
  return best;
}

/** Graph nodes a place's route may end at: its entrances, else the nearest node to it. [{ node, mapped }] */
export function goalsFor(g, place, { stepFree = false } = {}) {
  const ent = g.entrances.get(place.osm);
  if (ent?.length) return ent.filter(e => g.adj[e.node].some(i => usable(g.edges[i], stepFree)));
  const s = snap(g, place.x, place.z, { stepFree, reach: (place.r ?? 0) + SNAP_M });
  if (!s) return [];
  const e = g.edges[s.edge];
  return [{ node: s.t < 0.5 ? e.a : e.b, mapped: false }];
}

// a small binary heap of [priority, value]
function heap() {
  const h = [];
  return {
    get size() { return h.length; },
    push(p, v) {
      h.push([p, v]); let i = h.length - 1;
      while (i > 0) { const j = (i - 1) >> 1; if (h[j][0] <= h[i][0]) break; [h[i], h[j]] = [h[j], h[i]]; i = j; }
    },
    pop() {
      const top = h[0], last = h.pop();
      if (h.length) {
        h[0] = last; let i = 0;
        for (;;) {
          const l = 2 * i + 1, r = l + 1; let m = i;
          if (l < h.length && h[l][0] < h[m][0]) m = l;
          if (r < h.length && h[r][0] < h[m][0]) m = r;
          if (m === i) break; [h[i], h[m]] = [h[m], h[i]]; i = m;
        }
      }
      return top;
    },
  };
}

/**
 * A walking route from (x, z) to a place. Returns null when there is none, else
 * { points: [[x, z], ...] from the start to the goal, length (metres walked), goal: { node, mapped },
 *   steps (true if any stairs on the way), steep (true if any stretch steeper than the ramp limit),
 *   street (metres along streets), offPath (metres from the start to the nearest path) }.
 * stepFree: no stairs and nothing steeper than paths.json's steep_pct.
 */
export function route(g, from, place, { stepFree = false } = {}) {
  const goals = goalsFor(g, place, { stepFree });
  const start = snap(g, from.x, from.z, { stepFree });
  if (!goals.length || !start) return null;
  const isGoal = new Map(goals.map(o => [o.node, o]));
  const h = i => { let m = Infinity; for (const o of goals) m = Math.min(m, Math.hypot(g.x[i] - g.x[o.node], g.z[i] - g.z[o.node])); return m; };
  const n = g.x.length, dist = new Float64Array(n).fill(Infinity), via = new Int32Array(n).fill(-1);
  const se = g.edges[start.edge], q = heap();
  // the start lies on an edge: both its ends are reachable for part of its cost
  for (const [node, part] of [[se.a, start.t], [se.b, 1 - start.t]]) {
    const d = cost(se) * part;
    if (d < dist[node]) { dist[node] = d; via[node] = -2; q.push(d + h(node), node); }
  }
  let end = -1;
  while (q.size) {
    const [, i] = q.pop();
    if (isGoal.has(i)) { end = i; break; }
    for (const ei of g.adj[i]) {
      const e = g.edges[ei];
      if (!usable(e, stepFree)) continue;
      const j = e.a === i ? e.b : e.a, d = dist[i] + cost(e);
      if (d < dist[j]) { dist[j] = d; via[j] = ei; q.push(d + h(j), j); }
    }
  }
  if (end < 0) return null;
  const nodes = [end], used = [];
  for (let i = end; via[i] >= 0;) { const e = g.edges[via[i]]; used.push(e); i = e.a === i ? e.b : e.a; nodes.push(i); }
  nodes.reverse(); used.reverse();
  const points = [[start.x, start.z], ...nodes.map(i => [g.x[i], g.z[i]])];
  // the walk from the snap point along the start edge is part of the route
  let length = Math.hypot(start.x - g.x[nodes[0]], start.z - g.z[nodes[0]]), street = se.flags & STREET ? length : 0;
  let steps = false, steep = false;
  for (const e of [se, ...used]) { steps ||= !!(e.flags & STEPS); steep ||= !!(e.flags & STEEP); }
  for (const e of used) { length += e.length; if (e.flags & STREET) street += e.length; }
  if (points.length > 1 && points[0][0] === points[1][0] && points[0][1] === points[1][1]) points.shift();
  return { points, length, goal: isGoal.get(end), steps, steep, street, offPath: start.distance };
}

/** Walking time in whole minutes at 1.3 m/s (a relaxed pace), at least 1. */
export function walkMinutes(metres) {
  return Math.max(1, Math.round(metres / 1.3 / 60));
}
