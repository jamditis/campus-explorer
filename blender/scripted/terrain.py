"""Ground heights for the southwest build. numpy only (no bpy), so it can be tested outside Blender.

Heights are 3DEP LiDAR ground (class 2) returns on a 1 m grid. Soft ground follows them, lightly
smoothed.
Paving does not: a road is a graded surface, so paved ground is smoothed over 5 m using paved cells
only
(a bank or a planting bed beside the road does not pull it up or down). Without that, the noise of a
few
LiDAR returns per square metre shows as lumps in roads and walks.
"""

import geom
import numpy as np

BLEND = 4.0  # width of the band along the footprint edge that blends into the neighbours' ground
GRADE = 5.0  # smoothing length of paved ground, metres
GRADE_RIDGE = 0.3  # cells squared: how firmly a slope paved cells hardly show is held level
GRADE_LEVEL = 1.0  # metres: paving this far above or below a cell counts less in its grade
REACH = 6.0  # an edge sample speaks for ground within this distance of it, metres
SEAM = 0.15  # paving meets a neighbour flush only when they are this close in height already
LEVEL_PCT = 10  # percentile of the shore's ground that sets a water level (see shore_level)
CAP_GAP = 0.03  # ground held this far below a cap's top (the rows of a seating bowl)
CAP_EDGE = 0.05  # a point this close to a cap's outline is held by it too
EDGE_RUN = (
    12  # edge samples (1 m apart) averaged each side, so the blended edge has no lumps either
)
HEIGHT_RUN = 3  # edge samples averaged each side where the neighbour is met as a height
RUN_STEP = 1.5  # edge samples further apart than this are not one run (edge.py: 1 m apart)
RUN_DZ = 0.3  # metres: nor are two samples whose heights jump by more (two meshes meet there)
FOLLOW_TOL = 0.05  # metres: a neighbour this close to following the LiDAR is met as an offset
# Where the LiDAR runs on across the edge with no step (a road cut, not a wall or a bank), a
# step to the neighbour is the neighbour's error (a coarse skirt or far-field ground): the ground
# there, paving too, ramps to meet it, no steeper than RAMP_GRADE and over at most RAMP_MAX.
REAL_STEP = 0.25  # metres: a step the LiDAR shows across the edge larger than this is real
ACROSS = (2.0, 6.0)  # metres from the edge, each side, over which the LiDAR's step is read
RAMP_GRADE = 0.06  # mean slope of a ramp to a neighbour
RAMP_MAX = 30.0  # metres: the longest ramp
CUT_DEPTH = 8.0  # metres in from the edge over which a cut's paving is read
CUT_SHARE = 0.6  # paved share of CUT_DEPTH (paved 1 m in too) that makes a cut: a road crossing
# the edge, also at a slant; a drive or a walk along the edge is not one
CUT_SPREAD = 4  # samples each side over which a cut's ramp and share are spread along the edge


def _blur(a, sigma):
    """Separable Gaussian blur with edge padding."""
    r = max(1, int(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    p = np.pad(a, r, mode="edge")
    p = np.apply_along_axis(lambda v: np.convolve(v, k, mode="valid"), 0, p)
    return np.apply_along_axis(lambda v: np.convolve(v, k, mode="valid"), 1, p)


def _fill(a):
    """Fill empty cells with the mean of their filled neighbours, pass after pass."""
    a = a.copy()
    while np.isnan(a).any() and np.isfinite(a).any():
        p = np.pad(a, 1, constant_values=np.nan)
        stack = np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
        n = np.isfinite(stack).sum(0)
        mean = np.nansum(stack, 0) / np.maximum(n, 1)
        m = np.isnan(a) & (n > 0)
        a[m] = mean[m]
    return a


def _inside(ring, px, py):
    """Vectorised even-odd test of points against one closed outline."""
    r = np.asarray(ring)
    hit = np.zeros(len(px), bool)
    ax, ay = r[:, 0], r[:, 1]
    bx, by = np.roll(ax, -1), np.roll(ay, -1)
    for i in range(len(r)):
        if ay[i] == by[i]:
            continue
        cross = ((ay[i] > py) != (by[i] > py)) & (
            px < ax[i] + (py - ay[i]) * (bx[i] - ax[i]) / (by[i] - ay[i])
        )
        hit ^= cross
    return hit


def _edge_distance(ring, px, py):
    """Distance from each point to the nearest edge of a closed outline."""
    r = np.asarray(ring)
    best = np.full(len(px), np.inf)
    for a, b in zip(r, np.roll(r, -1, 0), strict=True):
        d = b - a
        ln = float(d @ d) or 1e-12
        t = np.clip(((px - a[0]) * d[0] + (py - a[1]) * d[1]) / ln, 0, 1)
        best = np.minimum(best, np.hypot(px - (a[0] + t * d[0]), py - (a[1] + t * d[1])))
    return best


def _normals(ring, px, py):
    """Outward unit normal of a closed outline at each point, from its nearest edge."""
    r = np.asarray(ring, float)
    sign = 1.0 if geom.area([tuple(p) for p in r]) > 0 else -1.0  # anticlockwise: right is out
    best, out = np.full(len(px), np.inf), np.zeros((len(px), 2))
    for a, b in zip(r, np.roll(r, -1, 0), strict=True):
        d = b - a
        ln = float(np.hypot(*d)) or 1e-12
        t = np.clip(((px - a[0]) * d[0] + (py - a[1]) * d[1]) / ln**2, 0, 1)
        dist = np.hypot(px - (a[0] + t * d[0]), py - (a[1] + t * d[1]))
        hit = dist < best
        best[hit] = dist[hit]
        out[hit] = sign * np.array([d[1], -d[0]]) / ln
    return out


def _cells(rings, x0, y1, nx, ny, cell):
    """Grid cells (row 0 north) whose centres lie inside any of the closed outlines."""
    out = np.zeros((ny, nx), bool)
    cx, cy = x0 + (np.arange(nx) + 0.5) * cell, y1 - (np.arange(ny) + 0.5) * cell
    for ring in rings:
        r = np.asarray(ring, float)
        ci = np.nonzero((cx >= r[:, 0].min()) & (cx <= r[:, 0].max()))[0]
        cj = np.nonzero((cy >= r[:, 1].min()) & (cy <= r[:, 1].max()))[0]
        if not len(ci) or not len(cj):
            continue
        gx, gy = np.meshgrid(cx[ci], cy[cj])
        hit = _inside(r, gx.ravel(), gy.ravel()).reshape(gx.shape)
        out[np.ix_(cj, ci)] |= hit
    return out


def _masked_blur(a, mask, sigma):
    """Gaussian blur of `a` that uses the cells of `mask` only. NaN where no masked cell is near."""
    w = _blur(mask.astype(float), sigma)
    return np.where(w > 0.02, _blur(np.where(mask, a, 0.0), sigma) / np.maximum(w, 1e-9), np.nan)


def _masked_plane(a, mask, sigma, ridge=GRADE_RIDGE, level=GRADE_LEVEL, data=None, ref=None):
    """Graded paving: each masked cell takes the value at its centre of a plane fitted to the
    masked cells round it, weighted by distance (Gaussian, `sigma` cells, out to 2.5 sigma) and by
    height (Gaussian, `level` metres, against `ref`, the cell's own lightly smoothed ground; `a`
    if not given). Only cells of `data` (the masked cells with LiDAR ground returns of their own)
    give heights: under a stand's void the ground is a guess filled in from round it.

    - A plane, not a mean: where the masked cells lie on one side only (the end of a drive or a
      walk, a lot's edge, a strip that stops at the footprint) a mean is the height of a point
      inside the paving, up or down the slope; a plane is not. Inside a wide paved area the two
      are the same smoothing, which takes the LiDAR noise out of roads.
    - Weighted by height: paving on another level nearby (a lot below a bank, a walk on top of
      one) does not tilt the plane. A road's own cells up or down its slope keep most weight.
    - `ridge` (cells squared, times the weight) holds a slope the cells hardly show (across a
      strip one or two cells wide) toward level.
    A cell next to the mask carries on the slope of the two cells beside it (two rings), so the
    paving's edge reads between them; farther cells are NaN."""
    ny, nx = a.shape
    data = mask if data is None else mask & data
    ref = a if ref is None else ref
    za = np.where(data, a, np.nan)
    rr = int(np.ceil(2.5 * sigma))
    zp = np.pad(za, rr, constant_values=np.nan)
    acc = np.zeros((9, ny, nx))
    for dj in range(-rr, rr + 1):
        for di in range(-rr, rr + 1):
            d2 = di * di + dj * dj
            if d2 > rr * rr:
                continue
            zs = zp[rr + dj : rr + dj + ny, rr + di : rr + di + nx]
            dz = zs - ref
            w = np.exp(-0.5 * d2 / sigma**2) * np.exp(-0.5 * (dz / level) ** 2)
            w = np.where(np.isfinite(w), w, 0.0)
            dz = np.where(np.isfinite(dz), dz, 0.0)
            wz = w * dz
            for k, q in enumerate((w, w * di, w * dj, w * di * di, w * di * dj, w * dj * dj)):
                acc[k] += q
            acc[6] += wz
            acc[7] += wz * di
            acc[8] += wz * dj
    s0, su, sv, suu, suv, svv, sz, suz, svz = acc
    ok = mask & (s0 > 1e-6)
    mat = np.stack(
        [
            np.stack([s0, su, sv], -1),
            np.stack([su, suu + ridge * s0, suv], -1),
            np.stack([sv, suv, svv + ridge * s0], -1),
        ],
        -2,
    )[ok]
    rhs = np.stack([sz, suz, svz], -1)[ok]
    out = np.full(a.shape, np.nan)
    out[ok] = np.linalg.solve(mat, rhs[..., None])[..., 0, 0] + ref[ok]
    done = ok.copy()
    for _ in range(2):  # two rings of cells round the paving
        p = np.pad(np.where(done, out, np.nan), 2, constant_values=np.nan)
        near = [p[1:-3, 2:-2], p[3:-1, 2:-2], p[2:-2, 1:-3], p[2:-2, 3:-1]]  # N S W E
        far = [p[:-4, 2:-2], p[4:, 2:-2], p[2:-2, :-4], p[2:-2, 4:]]
        # the slope of the two cells next to it carried on one cell, else the next cell's value
        pairs = zip(near, far, strict=True)
        stack = np.stack([np.where(np.isfinite(f), 2 * c - f, c) for c, f in pairs])
        n = np.isfinite(stack).sum(0)
        ring = ~done & (n > 0)
        out[ring] = (np.nansum(stack, 0) / np.maximum(n, 1))[ring]
        done |= ring
    return out


def _sample(a, x, y, x0, y1, cell):
    """Bilinear sample of a grid whose row 0 is the north edge; cell centres carry the values."""
    fx = np.clip((x - x0) / cell - 0.5, 0, a.shape[1] - 1.001)
    fy = np.clip((y1 - y) / cell - 0.5, 0, a.shape[0] - 1.001)
    i, j = fx.astype(int), fy.astype(int)
    tx, ty = fx - i, fy - j
    top = a[j, i] * (1 - tx) + a[j, i + 1] * tx
    bottom = a[j + 1, i] * (1 - tx) + a[j + 1, i + 1] * tx
    return top * (1 - ty) + bottom * ty


def _windows(e, kind=None, run=EDGE_RUN, dz=RUN_DZ):
    """Symmetric windows along the run of samples e (in footprint order, wrapping at the ends):
    for each sample the indices of the k <= `run` samples each side, where the run goes on
    unbroken both ways (no step over RUN_STEP: the old ground had none there, or the edge is
    shared with another scripted area; no jump of the neighbour's height over `dz` from one
    sample to the next: another mesh begins; and no change of `kind`). A run's end sample has
    k = 0."""
    n = len(e)
    step = np.hypot(*(np.roll(e[:, :2], -1, 0) - e[:, :2]).T)  # i to i + 1
    joined = step <= RUN_STEP
    if dz is not None:
        joined &= np.abs(np.roll(e[:, 2], -1) - e[:, 2]) <= dz
    if kind is not None:
        joined &= np.roll(kind, -1) == kind
    out = []
    for i in range(n):
        k = 0
        while k < run and k < (n - 1) // 2 and joined[(i - k - 1) % n] and joined[(i + k) % n]:
            k += 1
        out.append(np.arange(i - k, i + k + 1) % n)
    return out


def _follows(e, off, tol=FOLLOW_TOL):
    """Whether the neighbour follows the LiDAR at each sample: over its window, its offset from
    the LiDAR varies no more than its height strays from a straight line (plus `tol`)."""
    out = np.ones(len(e), bool)
    for i, idx in enumerate(_windows(e)):
        if len(idx) < 3:
            continue
        t = np.arange(len(idx), dtype=float)
        z = e[idx, 2]
        line = np.polyval(np.polyfit(t, z, 1), t)
        out[i] = off[idx].std() <= (z - line).std() + tol
    return out


def _run_mean(e, v, kind):
    """Mean of v over each sample's symmetric window (`_windows`): a sample at the end of a run
    keeps its own value; offsets and heights (`kind`) are not averaged together. Offsets (kind
    True: the LiDAR's noise is in them) are averaged over EDGE_RUN, heights (a coarse ground,
    smooth already) over HEIGHT_RUN only, so a coarse ground's bend round a corner stays."""
    long, short = _windows(e, kind), _windows(e, kind, run=HEIGHT_RUN)
    return np.array([v[a if k else b].mean() for a, b, k in zip(long, short, kind, strict=True)])


def shore_level(samples):
    """Water level from the ground read along a shore traced on the ortho.

    Where the trace lies on the water the LiDAR ground is the water surface (or, where water gave
    no return, the fill from the lowest ground round it); where it drifts onto the bank it is
    higher, never lower except by noise. So a low percentile reads the waterline: the median would
    climb the bank wherever half the trace drifts landward, the minimum would take one stray low
    return. With one sample a metre, a shore of 30 m or more has three or more samples under it.
    """
    return float(np.percentile(np.asarray(samples, float), LEVEL_PCT))


def flood(z, tris, owner, levels):
    """Vertex heights with every vertex of a water triangle set to its water body's level.

    `levels` maps a surface index (as in `owner`) to its level. The shore vertices are shared with
    the ground round the water, so that ground comes down (or up) to the waterline in the same
    mesh: no crack and no wall.
    """
    out = np.array(z, float)
    for i, lv in levels.items():
        out[np.unique(tris[owner == i])] = lv
    return out


class Terrain:
    """Ground height for soft ground (`rough`) and for paving (`graded`), with lifts and the edge
    blend.

    edge       [x, y, z] along the footprint, in order: the neighbours' ground there
    (<area>/edge_heights.json)
    lifts      the plan's `lifts`
    footprint  closed outline of the build; the edge blend acts within BLEND of it
    paved      outlines of the paved surfaces (roads, lots, walks, turf): the cells that grade
    together
    roads      outlines of the paving that may ramp to a coarse neighbour where it crosses the edge
    (the plan's `"road": true`); without any, the road-cut rule does nothing
    """

    def __init__(
        self,
        lidar_npz,
        edge=None,
        lifts=(),
        footprint=None,
        paved=(),
        voids=(),
        cell=1.0,
        caps=(),
        roads=(),
    ):
        self.lifts, self.footprint, self.caps = list(lifts), footprint, list(caps)
        z = np.load(lidar_npz)
        self.x0, self.y0, self.x1, self.y1 = (float(v) for v in z["box"][:4])
        self.cell = cell
        pts = z["pts"]
        g = pts[pts[:, 3] == 2]
        # A solid grandstand is classed as ground in the point cloud: its seating deck would become
        # a
        # bank. Ground returns inside `voids` (the stands' outlines) are left out and the gap is
        # filled
        # from the ground around it.
        for ring in voids:
            g = g[~_inside(ring, g[:, 0], g[:, 1])]
        nx, ny = round((self.x1 - self.x0) / cell), round((self.y1 - self.y0) / cell)
        col = np.clip(((g[:, 0] - self.x0) / cell).astype(int), 0, nx - 1)
        row = np.clip(((self.y1 - g[:, 1]) / cell).astype(int), 0, ny - 1)
        s, n = np.zeros((ny, nx)), np.zeros((ny, nx))
        np.add.at(s, (row, col), g[:, 2])
        np.add.at(n, (row, col), 1)
        # cells with ground returns of their own, or next to one (under a roof or a stand there is
        # none: the filled ground there is a guess, and an edge sample is not read against it)
        p = np.pad(n > 0, 1)
        self.measured = np.zeros((ny, nx), bool)
        for dj in range(3):
            for di in range(3):
                self.measured |= p[dj : dj + ny, di : di + nx]
        base = _fill(np.where(n > 0, s / np.maximum(n, 1), np.nan))
        self.base = base  # unsmoothed 1 m ground: water levels are read from it
        self.rough = _blur(base, 1.0)
        self.graded = _blur(base, 2.5)
        self.paved = np.zeros((ny, nx), bool)  # the paved cells
        self.roads = list(roads)  # the plan's "road": true surfaces, the only ones that ramp
        self.road_cells = _cells(self.roads, self.x0, self.y1, nx, ny, cell)
        if paved:
            cx = self.x0 + (np.arange(nx) + 0.5) * cell
            cy = self.y1 - (np.arange(ny) + 0.5) * cell
            gx, gy = (v.ravel() for v in np.meshgrid(cx, cy))
            mask = np.zeros(nx * ny, bool)
            for ring in paved:
                r = np.asarray(ring)
                box = (
                    (gx >= r[:, 0].min())
                    & (gx <= r[:, 0].max())
                    & (gy >= r[:, 1].min())
                    & (gy <= r[:, 1].max())
                )
                idx = np.nonzero(box)[0]
                mask[idx[_inside(ring, gx[idx], gy[idx])]] = True
            mask = self.paved = mask.reshape(ny, nx)
            only = _masked_plane(base, mask, GRADE / cell, data=n > 0, ref=self.rough)
            # paving under a stand (a void: its ground is filled in from round the stand, and the
            # bowl hides it) keeps the plain mean over the paving round it, as before
            blind = np.zeros(nx * ny, bool)
            for ring in voids:
                blind |= _inside(ring, gx, gy)
            blind = mask & blind.reshape(ny, nx)
            only[blind] = _masked_blur(base, mask, GRADE / cell)[blind]
            self.graded = np.where(np.isfinite(only), only, self.graded)
        self.edge, self.relative = None, None
        if edge:
            e = np.array(edge, float).reshape(-1, 3)
            # A sample is kept as the neighbour's offset from the LiDAR ground under it, so the
            # edge keeps the real relief along it (a bank up to a bridge end, a cross-slope) and a
            # sample a few metres away round a corner adds only its offset, not its height. Where
            # the LiDAR has no ground under a sample (a roof, a stand), its height is used as is.
            i = np.clip(((e[:, 0] - self.x0) / cell).astype(int), 0, nx - 1)
            j = np.clip(((self.y1 - e[:, 1]) / cell).astype(int), 0, ny - 1)
            ground = _sample(self.rough, e[:, 0], e[:, 1], self.x0, self.y1, cell)
            # A neighbour that does not follow the LiDAR (a coarse skirt over a bank) is met as a
            # height: there its offset swings along the run more than its height strays from a
            # straight line.
            rel = self.measured[j, i] & _follows(e, e[:, 2] - ground)
            v = np.where(rel, e[:, 2] - ground, e[:, 2])
            e[:, 2] = _run_mean(e, v, rel) if EDGE_RUN > 0 else v
            self.edge, self.relative = e, rel
            self.ramp, self.free = np.full(len(e), BLEND), np.zeros(len(e))
            if footprint is not None and self.roads:
                self._ramps(np.where(rel, ground + e[:, 2], e[:, 2]))

    def _ramps(self, nbz):
        """Per edge sample: how far in the ground ramps to the neighbour (`ramp`, metres) and how
        much paving meets it (`free`, 0 to 1). Paving meets where the LiDAR shows no step across
        the edge (a road that runs on, met by a coarse ground): a step to the neighbour there is
        the neighbour's error. Where the LiDAR shows one (a wall, a bank) or does not reach past
        the edge, paving keeps its grade. Both only at a cut, where a road (`roads`) crosses the
        edge, and the soft ground beside it ramps with it; elsewhere soft ground bends over
        BLEND as before (a coarse skirt over a hill must not flatten the hill). Both are spread
        along the run (`_windows`), first widened, so neither changes in a jump from one sample
        to the next and a cut meets in full across its whole width."""
        e = self.edge
        nrm = _normals(self.footprint, e[:, 0], e[:, 1])
        real = self.step_across(e[:, 0], e[:, 1], nrm)
        step = nbz - self.z(e[:, 0], e[:, 1], True)
        free = np.abs(np.nan_to_num(real, nan=np.inf)) < REAL_STEP  # the LiDAR runs on level
        # a cut: a road ("road": true) runs on in from the edge
        ny, nx = self.paved.shape
        depth = np.arange(1.0, CUT_DEPTH + 0.5)
        hits = np.zeros((len(e), len(depth)), bool)
        for c, t in enumerate(depth):
            i = np.clip(((e[:, 0] - t * nrm[:, 0] - self.x0) / self.cell).astype(int), 0, nx - 1)
            j = np.clip(((self.y1 - e[:, 1] + t * nrm[:, 1]) / self.cell).astype(int), 0, ny - 1)
            hits[:, c] = self.road_cells[j, i]
        cut = free & hits[:, 0] & (hits.mean(1) >= CUT_SHARE)
        length = np.where(cut, np.clip(np.abs(step) / RAMP_GRADE, BLEND, RAMP_MAX), BLEND)
        wins = _windows(e, run=CUT_SPREAD, dz=None)
        widest = np.array([length[w].max() for w in wins])
        wider = np.array([cut[w].max() for w in wins], float)
        self.ramp = np.array([widest[w].mean() for w in wins])
        self.free = np.array([wider[w].mean() for w in wins])

    def step_across(self, x, y, n):
        """The step the LiDAR shows across an edge at each point (n: outward unit normals): the
        soft ground ACROSS metres out, fitted with a line and read at the edge, less the same
        inside. NaN where the LiDAR does not reach (outside its box, or no returns near)."""
        t = np.linspace(*ACROSS, 5)
        sides = []
        for sign in (1.0, -1.0):
            px = x[:, None] + sign * t[None, :] * n[:, 0, None]
            py = y[:, None] + sign * t[None, :] * n[:, 1, None]
            ny, nx = self.measured.shape
            i = np.floor((px - self.x0) / self.cell).astype(int)
            j = np.floor((self.y1 - py) / self.cell).astype(int)
            box = (i >= 0) & (i < nx) & (j >= 0) & (j < ny)
            ok = box & self.measured[np.clip(j, 0, ny - 1), np.clip(i, 0, nx - 1)]
            z = _sample(self.rough, px.ravel(), py.ravel(), self.x0, self.y1, self.cell)
            z = np.where(ok, z.reshape(px.shape), np.nan)
            # least-squares line through the measured points, read at the edge (t = 0)
            w = ok.astype(float)
            sw, st, stt = w.sum(1), (w * t).sum(1), (w * t * t).sum(1)
            sz, stz = np.nansum(z, 1), np.nansum(z * t, 1)
            det = sw * stt - st * st
            at0 = (stt * sz - st * stz) / np.where(det > 1e-9, det, np.nan)
            sides.append(np.where(sw >= 3, at0, np.nan))
        return sides[0] - sides[1]

    def z(self, x, y, smooth=False):
        """Height before the edge blend: graded (`smooth`) or soft ground, plus the lifts."""
        x, y = np.asarray(x, float), np.asarray(y, float)
        a = self.graded if smooth else self.rough
        return _sample(a, x, y, self.x0, self.y1, self.cell) + self.lift(x, y)

    def surface(self, x, y, paved, capped=True):
        """Finished height of points: `paved` (bool per point) picks graded ground; blended at the
        edge; held under the caps unless `capped` is False (the ground outside a bowl, which meets
        the bowl's outline at its own height).
        """
        x, y = np.asarray(x, float), np.asarray(y, float)
        z = np.where(paved, self.z(x, y, True), self.z(x, y, False))
        if self.footprint is not None and self.edge is not None:
            z = self._blend(x, y, z, paved)
        return self.cap(x, y, z) if capped else z

    def under_caps(self, x, y):
        """Whether points (triangle centres) lie inside a cap's outline."""
        hit = np.zeros(len(x), bool)
        for c in self.caps:
            hit |= _inside(c["ring"], np.asarray(x, float), np.asarray(y, float))
        return hit

    def cap(self, x, y, z):
        """Heights held below the caps: inside a cap's ring, or on it (within CAP_EDGE: two
        sections' outlines that nearly meet leave ground vertices just off each), never above its
        top less CAP_GAP. Elsewhere nothing changes. A cap is {"ring", "top"}, `top` a function of
        x and y (stand.bowl_top): a seating bowl's rows and walkways."""
        z = np.array(z, float)
        for c in self.caps:
            m = _inside(c["ring"], x, y) | (_edge_distance(c["ring"], x, y) < CAP_EDGE)
            if m.any():
                z[m] = np.minimum(z[m], np.asarray(c["top"](x[m], y[m]), float) - CAP_GAP)
        return z

    def _blend(self, x, y, z, paved):
        """The edge blend: soft ground bends to the neighbours' ground over BLEND, or over the
        nearest sample's `ramp` where that is longer. Paving bends where the two are nearly level
        already (within SEAM), and by the sample's `free` share where the LiDAR shows no step
        across the edge, on `roads` only: a road must not climb a bank that stands beside it,
        but a flagged road that runs on into a coarse neighbour meets it."""
        paved = np.broadcast_to(np.asarray(paved, bool), np.shape(x))
        d = _edge_distance(self.footprint, x, y)
        n = len(x)
        step, at_s, length, free = (np.full(n, v) for v in (np.nan, 0.0, BLEND, 0.0))
        idx = np.nonzero(d < max(BLEND, float(self.ramp.max(initial=BLEND))))[0]
        near = self._nearest(x[idx], y[idx], d[idx])
        k, s = idx[near >= 0], near[near >= 0]
        rel, ez = self.relative[s], self.edge[s, 2]
        here = _sample(self.rough, x[k], y[k], self.x0, self.y1, self.cell)
        step[k] = np.where(rel, here + ez, ez) - z[k]  # the neighbour less this ground, here
        # past BLEND a longer ramp carries the step at the sample (its neighbour less this ground
        # there, of the point's kind) and eases it out: deep in a ramp this ground keeps its own
        # shape and only the edge's step fades
        sx, sy = self.edge[s, 0], self.edge[s, 1]
        at_s[k] = np.where(rel, _sample(self.rough, sx, sy, self.x0, self.y1, self.cell) + ez, ez)
        at_s[k] -= np.where(paved[k], self.z(sx, sy, True), self.z(sx, sy, False))
        length[k], free[k] = self.ramp[s], self.free[s]

        def ease(u):
            u = np.clip(u, 0, 1)
            return u * u * (3 - 2 * u)

        wb, wl = ease(d / BLEND), ease(d / length)
        seam = np.abs(step) < SEAM
        dz = np.nan_to_num(step * (1 - wb) + at_s * (wb - wl))
        ask = paved & (free > 0)  # paving ramps by the cut's share only on a road
        road = np.zeros(int(ask.sum()), bool)
        for ring in self.roads:
            road |= _inside(ring, x[ask], y[ask])
        free[np.nonzero(ask)[0][~road]] = 0.0
        return z + dz * np.where(paved, np.maximum(free, seam), 1.0)

    def lift(self, x, y):
        """Height added by the plan's `lifts`: `dz` inside a ring, eased to zero over `feather`."""
        out = np.zeros(np.shape(x))
        for lf in self.lifts:
            d = np.where(_inside(lf["ring"], x, y), 0.0, _edge_distance(lf["ring"], x, y))
            t = np.clip(1 - d / lf.get("feather", 10.0), 0, 1)
            out += lf["dz"] * t * t * (3 - 2 * t)
        return out

    def neighbour_z(self, x, y):
        """Height of the neighbours' ground by the nearest edge sample, NaN where none is within
        REACH (an edge with no samples has no neighbour to meet): the soft ground here plus that
        sample's offset from the LiDAR, or the sample's own height where it lies over ground the
        LiDAR does not see. `_blend` eases it out over BLEND from the footprint edge.
        """
        if self.edge is None or not len(self.edge):
            return np.full(np.shape(x), np.nan)
        x, y = np.asarray(x, float), np.asarray(y, float)
        near = self._nearest(x, y)
        ok = near >= 0
        out = np.full(len(x), np.nan)
        s = near[ok]
        here = _sample(self.rough, x[ok], y[ok], self.x0, self.y1, self.cell)
        out[ok] = np.where(self.relative[s], here + self.edge[s, 2], self.edge[s, 2])
        return out

    def _nearest(self, x, y, edge_d=None):
        """Index of the nearest edge sample within REACH of each point, -1 where there is none.
        With `edge_d` (each point's distance to the footprint) a sample with a longer `ramp`
        reaches that far, but no farther than REACH past the edge itself: a point by an edge
        with no samples (shared with another scripted area) takes none from along the edge."""
        out = np.empty(len(x), int)
        for k in range(0, len(x), 4096):  # in blocks, to bound the distance matrix
            d = (np.asarray(x)[k : k + 4096, None] - self.edge[None, :, 0]) ** 2 + (
                np.asarray(y)[k : k + 4096, None] - self.edge[None, :, 1]
            ) ** 2
            near = d.argmin(1)
            dist = np.sqrt(d[np.arange(len(near)), near])
            ok = dist <= REACH
            if edge_d is not None:
                reach = np.maximum(REACH, self.ramp[near])
                ok = (dist <= reach) & (dist <= np.asarray(edge_d)[k : k + 4096] + REACH)
            out[k : k + 4096] = np.where(ok, near, -1)
        return out

    def water_level(self, ring):
        """Level of a water body traced along its shore: `shore_level` of the unsmoothed ground
        read every metre along the outline."""
        pts = np.array([(p[0], p[1]) for p in geom.resample(list(ring), 1.0, True)])
        return shore_level(_sample(self.base, pts[:, 0], pts[:, 1], self.x0, self.y1, self.cell))

    def at(self, x, y):
        """Finished height of one point on paving (used to seat objects and curbs)."""
        return float(self.surface(np.array([x]), np.array([y]), np.array([True]))[0])
