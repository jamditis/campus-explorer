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
 * The nearest points on usable edges to (x, z), nearest first, at most `limit`, within `reach` metres:
 * [{ edge, t, x, z, distance }]. `t` runs from the edge's a (0) to b (1).
 */
export function snaps(g, x, z, { stepFree = false, reach = SNAP_M, limit = 6 } = {}) {
  const out = [];
  g.edges.forEach((e, i) => {
    if (!usable(e, stepFree)) return;
    const ax = g.x[e.a], az = g.z[e.a], dx = g.x[e.b] - ax, dz = g.z[e.b] - az;
    const len2 = dx * dx + dz * dz;
    const t = len2 > 0 ? Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / len2)) : 0;
    const px = ax + t * dx, pz = az + t * dz, d = Math.hypot(x - px, z - pz);
    if (d <= reach) out.push({ edge: i, t, x: px, z: pz, distance: d });
  });
  return out.sort((p, q) => p.distance - q.distance).slice(0, limit);
}

/** The nearest point on a usable edge, or null past `reach` metres. */
export function snap(g, x, z, opts = {}) {
  return snaps(g, x, z, { ...opts, limit: 1 })[0] ?? null;
}

/**
 * Where a place's route may end: its entrances ({ node, mapped }), else the nearest point on a path to it
 * ({ edge, t, x, z, mapped: false }).
 */
export function goalsFor(g, place, { stepFree = false } = {}) {
  const ent = g.entrances.get(place.osm);
  if (ent?.length) return ent.filter(e => g.adj[e.node].some(i => usable(g.edges[i], stepFree)));
  const s = snap(g, place.x, place.z, { stepFree, reach: (place.r ?? 0) + SNAP_M });
  return s ? [{ edge: s.edge, t: s.t, x: s.x, z: s.z, mapped: false }] : [];
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
 * { points: [[x, z], ...] from the start to the goal, length (metres walked), goal: { mapped, ... },
 *   steps (true if any stairs on the way), steep (true if any stretch steeper than the ramp limit),
 *   street (metres along streets), offPath (metres from (x, z) to where the route starts) }.
 * stepFree: no stairs and nothing steeper than paths.json's steep_pct. The start snaps to the nearest
 * usable path that reaches the place (up to six nearby edges are tried), so an unconnected scrap of
 * path next to the walker does not hide a route.
 */
export function route(g, from, place, { stepFree = false } = {}) {
  const goals = goalsFor(g, place, { stepFree });
  if (!goals.length) return null;
  for (const start of snaps(g, from.x, from.z, { stepFree })) {
    const r = search(g, start, goals, stepFree);
    if (r) return r;
  }
  return null;
}

function search(g, start, goals, stepFree) {
  const n = g.x.length, G = n; // G: one extra node that every goal leads to
  const at = o => (o.node !== undefined ? [g.x[o.node], g.z[o.node]] : [o.x, o.z]);
  const h = i => {
    if (i === G) return 0;
    let m = Infinity; for (const o of goals) { const [gx, gz] = at(o); m = Math.min(m, Math.hypot(g.x[i] - gx, g.z[i] - gz)); }
    return m;
  };
  // links into G: [node, cost, goal]
  const toGoal = new Map(), link = (i, c, o) => { if (!toGoal.has(i)) toGoal.set(i, []); toGoal.get(i).push([c, o]); };
  for (const o of goals) {
    if (o.node !== undefined) link(o.node, 0, o);
    else { const e = g.edges[o.edge]; link(e.a, cost(e) * o.t, o); link(e.b, cost(e) * (1 - o.t), o); }
  }
  const dist = new Float64Array(n + 1).fill(Infinity), via = new Int32Array(n + 1).fill(-1);
  let goalVia = null; // { node, goal } or { direct: goal }
  const se = g.edges[start.edge], q = heap();
  // the start lies on an edge: both its ends are reachable for part of its cost
  for (const [node, part] of [[se.a, start.t], [se.b, 1 - start.t]]) {
    const d = cost(se) * part;
    if (d < dist[node]) { dist[node] = d; via[node] = -2; q.push(d + h(node), node); }
  }
  // a goal on the start's own edge: walk straight along it
  for (const o of goals) {
    if (o.edge === start.edge) {
      const d = cost(se) * Math.abs(o.t - start.t);
      if (d < dist[G]) { dist[G] = d; goalVia = { direct: o }; q.push(d, G); }
    }
  }
  while (q.size) {
    const [, i] = q.pop();
    if (i === G) break;
    for (const [c, o] of toGoal.get(i) ?? []) {
      const d = dist[i] + c;
      if (d < dist[G]) { dist[G] = d; goalVia = { node: i, goal: o }; q.push(d, G); }
    }
    for (const ei of g.adj[i]) {
      const e = g.edges[ei];
      if (!usable(e, stepFree)) continue;
      const j = e.a === i ? e.b : e.a, d = dist[i] + cost(e);
      if (d < dist[j]) { dist[j] = d; via[j] = ei; q.push(d + h(j), j); }
    }
  }
  if (!goalVia) return null;
  const goal = goalVia.direct ?? goalVia.goal;
  const end = at(goal);
  let points, used = [];
  if (goalVia.direct) points = [[start.x, start.z], end];
  else {
    const nodes = [goalVia.node];
    for (let i = goalVia.node; via[i] >= 0;) { const e = g.edges[via[i]]; used.push(e); i = e.a === i ? e.b : e.a; nodes.push(i); }
    nodes.reverse(); used.reverse();
    points = [[start.x, start.z], ...nodes.map(i => [g.x[i], g.z[i]])];
    if (goal.node === undefined) points.push(end);
  }
  const ge = goal.edge !== undefined ? g.edges[goal.edge] : null;
  const legs = [se, ...used, ...(ge ? [ge] : [])];
  let length = 0, street = 0, steps = false, steep = false;
  for (let k = 1; k < points.length; k++) length += Math.hypot(points[k][0] - points[k - 1][0], points[k][1] - points[k - 1][1]);
  for (const e of used) if (e.flags & STREET) street += e.length;
  for (const e of legs) { steps ||= !!(e.flags & STEPS); steep ||= !!(e.flags & STEEP); }
  // drop repeated points (a start or goal exactly on a node)
  points = points.filter((p, k) => !k || p[0] !== points[k - 1][0] || p[1] !== points[k - 1][1]);
  return { points, length, goal, steps, steep, street, offPath: start.distance };
}

/** Walking time in whole minutes at 1.3 m/s (a relaxed pace), at least 1. */
export function walkMinutes(metres) {
  return Math.max(1, Math.round(metres / 1.3 / 60));
}
