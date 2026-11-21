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
REACH = 6.0  # an edge sample speaks for ground within this distance of it, metres
SEAM = 0.15  # paving meets a neighbour flush only when they are this close in height already
LEVEL_PCT = 10  # percentile of the shore's ground that sets a water level (see shore_level)
CAP_GAP = 0.03  # ground held this far below a cap's top (the rows of a seating bowl)
CAP_EDGE = 0.05  # a point this close to a cap's outline is held by it too
EDGE_RUN = (
    12  # edge samples (1 m apart) averaged each side, so the blended edge has no lumps either
)
RUN_STEP = 1.5  # edge samples further apart than this are not one run (edge.py: 1 m apart)
FOLLOW_TOL = 0.05  # metres: a neighbour this close to following the LiDAR is met as an offset


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


def _masked_blur(a, mask, sigma):
    """Gaussian blur of `a` that uses the cells of `mask` only. NaN where no masked cell is near."""
    w = _blur(mask.astype(float), sigma)
    return np.where(w > 0.02, _blur(np.where(mask, a, 0.0), sigma) / np.maximum(w, 1e-9), np.nan)


def _masked_plane(a, mask, sigma, ridge=GRADE_RIDGE):
    """Like `_masked_blur`, but each cell takes the value at its centre of a plane fitted to the
    masked cells round it (Gaussian weights): a local linear fit. Inside a wide paved area it is
    the same smoothing; where the masked cells lie on one side only (the end of a drive or walk, a
    lot's edge) a mean is pulled toward them, up or down the slope, and a plane is not. `ridge`
    (cells squared, times the weight) holds a slope that the cells hardly show (across a strip one
    or two cells wide) toward level, so it never amplifies the noise. NaN where no masked cell is
    near."""
    ny, nx = a.shape
    m = mask.astype(float)
    z0 = float(np.nanmean(a[mask])) if mask.any() else 0.0
    z = np.where(mask, a - z0, 0.0)
    v, u = np.mgrid[0:ny, 0:nx].astype(float)
    u -= nx / 2
    v -= ny / 2

    def b(q):
        return _blur(q, sigma)

    s0, su, sv = b(m), b(m * u), b(m * v)
    suu, suv, svv = b(m * u * u), b(m * u * v), b(m * v * v)
    sz, suz, svz = b(z), b(z * u), b(z * v)
    # moments about each cell's own centre
    cu, cv = su - u * s0, sv - v * s0
    cuu = suu - 2 * u * su + u * u * s0 + ridge * s0
    cvv = svv - 2 * v * sv + v * v * s0 + ridge * s0
    cuv = suv - u * sv - v * su + u * v * s0
    cuz, cvz = suz - u * sz, svz - v * sz
    mat = np.stack(
        [np.stack([s0, cu, cv], -1), np.stack([cu, cuu, cuv], -1), np.stack([cv, cuv, cvv], -1)],
        -2,
    )
    ok = s0 > 0.02
    rhs = np.stack([sz, cuz, cvz], -1)
    out = np.full(a.shape, np.nan)
    out[ok] = np.linalg.solve(mat[ok], rhs[ok][..., None])[..., 0, 0] + z0
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


def _windows(e, kind=None):
    """Symmetric windows along the run of samples e (in footprint order, wrapping at the ends):
    for each sample the indices of the k <= EDGE_RUN samples each side, where the run goes on
    unbroken both ways (no step over RUN_STEP: the old ground had none there, or the edge is
    shared with another scripted area; and no change of `kind`). A run's end sample has k = 0."""
    n = len(e)
    step = np.hypot(*(np.roll(e[:, :2], -1, 0) - e[:, :2]).T)  # i to i + 1
    joined = step <= RUN_STEP
    if kind is not None:
        joined &= np.roll(kind, -1) == kind
    out = []
    for i in range(n):
        k = 0
        while k < EDGE_RUN and k < (n - 1) // 2 and joined[(i - k - 1) % n] and joined[(i + k) % n]:
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
    keeps its own value; offsets and heights (`kind`) are not averaged together."""
    return np.array([v[idx].mean() for idx in _windows(e, kind)])


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
    """

    def __init__(
        self, lidar_npz, edge=None, lifts=(), footprint=None, paved=(), voids=(), cell=1.0, caps=()
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
            only = _masked_plane(base, mask.reshape(ny, nx), GRADE / cell)
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
        """The edge blend: soft ground (and nearly level paving) bends to the neighbours' ground."""
        d = _edge_distance(self.footprint, x, y)
        band = d < BLEND
        nb = np.full(len(x), np.nan)
        nb[band] = self.neighbour_z(x[band], y[band])
        t = np.clip(d / BLEND, 0, 1)
        w = t * t * (3 - 2 * t)
        # Soft ground bends to meet its neighbour. Paving does not, unless the two are nearly level
        # (a road that runs on into the next model): a road must not climb a bank that stands beside
        # it.
        meet = np.isfinite(nb) & (~np.asarray(paved, bool) | (np.abs(nb - z) < SEAM))
        return np.where(meet, nb * (1 - w) + z * w, z)

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

    def _nearest(self, x, y):
        """Index of the nearest edge sample within REACH of each point, -1 where there is none."""
        out = np.empty(len(x), int)
        for k in range(0, len(x), 4096):  # in blocks, to bound the distance matrix
            d = (np.asarray(x)[k : k + 4096, None] - self.edge[None, :, 0]) ** 2 + (
                np.asarray(y)[k : k + 4096, None] - self.edge[None, :, 1]
            ) ** 2
            near = d.argmin(1)
            out[k : k + 4096] = np.where(d[np.arange(len(near)), near] <= REACH**2, near, -1)
        return out

    def water_level(self, ring):
        """Level of a water body traced along its shore: `shore_level` of the unsmoothed ground
        read every metre along the outline."""
        pts = np.array([(p[0], p[1]) for p in geom.resample(list(ring), 1.0, True)])
        return shore_level(_sample(self.base, pts[:, 0], pts[:, 1], self.x0, self.y1, self.cell))

    def at(self, x, y):
        """Finished height of one point on paving (used to seat objects and curbs)."""
        return float(self.surface(np.array([x]), np.array([y]), np.array([True]))[0])
