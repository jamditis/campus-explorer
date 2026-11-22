"""Where two scripted areas share an edge, both ground meshes take the same vertices there and the
same heights. numpy only (no bpy).

Each area densifies its own outline (ground.GRID), so along a shared edge the two meshes would
put their vertices at different points, and each area reads its heights from its own LiDAR
raster and edge blend: two outlines that do not meet, a crack and a step of a few centimetres,
more on a steep bank. So each area's outline also takes the other areas' densified points that lie
on it (`points_on`), and the area built first records the heights of its outline vertices
(`Seam.record`); a later area takes those heights for the vertices it shares (`Seam.take`).
"""

import math

import geom
import numpy as np

TOL = 0.02  # metres: a point this close to an outline lies on it (geom.insert_on_ring's tolerance)
CELL = 0.05  # metres: the lookup grid of recorded vertices


def points_on(ring, others, step=2.0):
    """The points of the other areas' outlines, densified every `step` metres as the ground
    densifies its own (ground.triangulate), that lie within TOL of the closed outline `ring`."""
    ring = [(p[0], p[1]) for p in ring]
    n = len(ring)
    out = []
    for other in others:
        for x, y, _s in geom.resample([(p[0], p[1]) for p in other], step, True):
            for i in range(n):
                (ax, ay), (bx, by) = ring[i], ring[(i + 1) % n]
                dx, dy = bx - ax, by - ay
                ln2 = (dx * dx + dy * dy) or 1e-12
                t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ln2))
                if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= TOL * TOL:
                    out.append((x, y))
                    break
    return out


END = 0.25  # metres along the outline either side that must lie on the shared edge too


def _near(ring, x, y, tol=TOL):
    n = len(ring)
    for i in range(n):
        (ax, ay), (bx, by) = ring[i][:2], ring[(i + 1) % n][:2]
        dx, dy = bx - ax, by - ay
        ln2 = (dx * dx + dy * dy) or 1e-12
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ln2))
        if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= tol * tol:
            return True
    return False


def _along(ring, cum, total, s):
    """The point at arc length `s` (wrapped) along the closed outline `ring`."""
    s %= total
    i = int(np.searchsorted(cum, s, side="right") - 1)
    i = min(i, len(ring) - 1)
    (ax, ay), (bx, by) = ring[i], ring[(i + 1) % len(ring)]
    ln = cum[i + 1] - cum[i] or 1e-12
    t = (s - cum[i]) / ln
    return ax + t * (bx - ax), ay + t * (by - ay)


def ends(ring, others, step=END):
    """Points of the closed outline `ring`, `step` metres along it from each end of a stretch it
    shares with one of `others`, on the side that is not shared. At such an end the shared vertex
    takes the other area's height (the seam stays flush); the next vertex of this outline on its
    edge to the far field may be 2 m away, and the ground beside the far field climbed to that
    height over the whole run (up to 0.46 m in sw16 at village and west). A vertex here keeps
    this area's own height, so the change is held within `step`."""
    ring = [(p[0], p[1]) for p in ring]
    nxt = ring[1:] + ring[:1]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(ring, nxt, strict=True)]
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(cum[-1])

    def shared(x, y):
        return any(_near(o, x, y) for o in others)

    def arc(x, y):
        best, at = None, 0.0
        for i, (a, b) in enumerate(zip(ring, nxt, strict=True)):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln2 = (dx * dx + dy * dy) or 1e-12
            t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / ln2))
            d = (x - a[0] - t * dx) ** 2 + (y - a[1] - t * dy) ** 2
            if best is None or d < best:
                best, at = d, cum[i] + t * seg[i]
        return best, at

    # where a shared stretch can end: a corner of this outline on another one, or a corner of
    # another outline on this one
    cands = [p for p in ring if shared(*p)]
    for o in others:
        cands += [(p[0], p[1]) for p in o if arc(p[0], p[1])[0] <= TOL * TOL]
    out = []
    for x, y in cands:
        at = arc(x, y)[1]
        for s in (at - step, at + step):
            q = _along(ring, cum, total, s)
            if not shared(*q) and all(math.hypot(q[0] - r[0], q[1] - r[1]) > TOL for r in out):
                out.append(q)
    return out


def far_samples(samples, ring, others, near=None):
    """The edge samples ([x, y, ...] on the closed outline `ring`) that meet ground other than
    another scripted area's. A sample on an edge shared with one of `others`, or inside one, has no
    other model to meet and goes; the samples beside it, up to the end of the shared stretch,
    stay: there the far field begins (a three-way corner). sw16 dropped every sample within 2 m of
    another area, so the first 2 m of the far-field edges from a three-way corner met no far field
    (Lot 60 stood 0.40 m over it at its corner with the Village, (-212, 1281)). With `near` (metres)
    the sw16 rule: every sample within that distance of another area goes, for edge heights made
    the first way (a raster of tiles that still had their ground inside: near another area such a
    sample read that area's old ground, not the far field)."""
    out = []
    for e in samples:
        x, y = e[0], e[1]
        if any(_near(o, x, y, near or TOL) or geom.inside(o, x, y) for o in others):
            continue
        out.append(e)
    return out


def held_samples(samples, ring, others, holders, near=None):
    """The samples this area's paving keeps although the ground drops them: those an edge shared
    with one of `holders` (areas that came after this area's paving was reviewed and ask, with
    `"hold_neighbour_paving": true`, that it stay as it was) took away; the samples the other
    neighbours take stay gone. None when no holder is a neighbour (nothing held). Lots are only
    raised and reviewed paving does not move: the old samples bent this paving only where it was
    already within SEAM of them (terrain.Terrain `paving_edge`)."""
    if not holders:
        return None
    rest = [o for o in others if not any(o is h for h in holders)]
    return far_samples(samples, ring, rest, near)


def paving_samples(pave, edge, ring, others, holders, near=None):
    """The edge samples this area's paving is bent by (`terrain.Terrain` `paving_edge`), None
    where it takes the ground's. `pave` is the edge file's "paving" entry (samples and their
    source): the samples the reviewed paving was made with, kept when the file's samples were
    made again (sw18 read them 5 cm outside instead of 0.3 m; paving within 0.15 m of them would
    have moved), filtered as the ground's are; without it, `edge` (the ground's samples, read
    with `near`). Where a later neighbour holds this area's paving (`holders`, seam.held_samples)
    the samples its edge takes away stay too."""
    if pave:
        src = pave["samples"]
        near = None if "outside" in pave.get("source", "") else 2.0
    else:
        src = edge
    if holders:
        return held_samples(src, ring, others, holders, near)
    if pave:
        return far_samples(src, ring, others, near)
    return None


def taken(known, own, lot, old, keep=None):
    """Which vertices on a shared edge take the first-built area's height `known` (NaN: none)
    instead of their `own`: all of them, except a vertex of lot paving (`lot`: graded paving that
    is not a road) the shared height would lower, unless sw17's seam gave it that height already
    (`old`: a vertex both meshes had before either took the other's, at a densified outline
    point). Lots are only raised (AGENTS rule 6): the first area's height at a vertex only the
    later mesh had, or along its edge, lowered lots by up to 7 cm and a road by 0.33 m. A vertex
    of `keep` (paving held at a `level`: another model's landing the ground must meet) keeps its
    own height; the first area's edge skirt closes the step there."""
    known, own = np.asarray(known, float), np.asarray(own, float)
    ok = np.isfinite(known)
    lower = ok & (known < own - 1e-6)
    got = ok & ~(lower & np.asarray(lot, bool) & ~np.asarray(old, bool))
    return got if keep is None else got & ~np.asarray(keep, bool)


ECELL = 2.0  # metres: the lookup grid of recorded outline edges


class Seam:
    """Heights of outline vertices and edges, shared between the areas of one build.

    The first-built area's mesh may have vertices on a shared edge that the outline points of
    `points_on` do not give (a corner of one of its surfaces on the outline), and a later area
    has some of its own there too (an end point of `ends`, its own surfaces): either mesh's
    edge then ran straight past a vertex of the other, a step of up to 0.4 m in sw17. A later
    area therefore puts the first areas' recorded vertices on its outline (`on_ring`), and its
    vertices that meet no recorded vertex take the height of the recorded edge they lie on
    (`along`): its edge there lies on the first mesh's edge."""

    def __init__(self):
        self.cells = {}
        self.edges = {}

    def record(self, xy, z, edges=()):
        """Keep the heights `z` of the vertices `xy` (n x 2), and the mesh's outline edges among
        them (`edges`: index pairs into `xy`); a vertex already recorded keeps its first height."""
        xy, z = np.asarray(xy, float), np.asarray(z, float)
        for (x, y), h in zip(xy, z, strict=True):
            key = (round(x / CELL), round(y / CELL))
            self.cells.setdefault(key, []).append((x, y, float(h)))
        for i, j in edges:
            seg = (*xy[i], z[i], *xy[j], z[j])
            lo, hi = np.minimum(xy[i], xy[j]) - TOL, np.maximum(xy[i], xy[j]) + TOL
            for gx in range(math.floor(lo[0] / ECELL), math.floor(hi[0] / ECELL) + 1):
                for gy in range(math.floor(lo[1] / ECELL), math.floor(hi[1] / ECELL) + 1):
                    self.edges.setdefault((gx, gy), []).append(seg)

    def along(self, xy):
        """The height of the nearest recorded edge within TOL of each point of `xy`, at the point
        (linear along the edge), NaN where none is."""
        xy = np.asarray(xy, float)
        out = np.full(len(xy), np.nan)
        for k, (x, y) in enumerate(xy):
            best = TOL * TOL + 1e-12
            for ax, ay, az, bx, by, bz in self.edges.get(
                (math.floor(x / ECELL), math.floor(y / ECELL)), ()
            ):
                dx, dy = bx - ax, by - ay
                ln2 = dx * dx + dy * dy
                if ln2 < 1e-12:
                    continue
                t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ln2))
                d = (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2
                if d < best:
                    best, out[k] = d, az + t * (bz - az)
        return out

    def on_ring(self, ring, skip=()):
        """The recorded vertices that lie within TOL of the closed outline `ring`, leaving out any
        within TOL of a point of `skip` (points the outline takes already)."""
        ring = [(p[0], p[1]) for p in ring]
        skip = [(p[0], p[1]) for p in skip]
        lo = np.min(ring, 0) - TOL
        hi = np.max(ring, 0) + TOL
        out = []
        for pts in self.cells.values():
            for x, y, _h in pts:
                if not (lo[0] <= x <= hi[0] and lo[1] <= y <= hi[1]) or not _near(ring, x, y):
                    continue
                if any((x - px) ** 2 + (y - py) ** 2 <= TOL * TOL for px, py in skip + out):
                    continue
                out.append((x, y))
        return out

    def take(self, xy):
        """The recorded height within TOL of each point of `xy`, NaN where none is."""
        xy = np.asarray(xy, float)
        out = np.full(len(xy), np.nan)
        for k, (x, y) in enumerate(xy):
            cx, cy = round(x / CELL), round(y / CELL)
            best = TOL * TOL + 1e-12  # strictly nearer: of two at one point, the first wins
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    for px, py, h in self.cells.get((cx + i, cy + j), ()):
                        d = (px - x) ** 2 + (py - y) ** 2
                        if d < best:
                            best, out[k] = d, h
        return out
