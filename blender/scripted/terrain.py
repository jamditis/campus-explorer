"""Ground heights for the southwest build. numpy only (no bpy), so it can be tested outside Blender.

Heights are 3DEP LiDAR ground (class 2) returns on a 1 m grid. Soft ground follows them, lightly
smoothed.
Paving does not: a road is a graded surface, so paved ground is smoothed over 5 m using paved cells
only
(a bank or a planting bed beside the road does not pull it up or down). Without that, the noise of a
few
LiDAR returns per square metre shows as lumps in roads and walks.
"""

import numpy as np

BLEND = 4.0  # width of the band along the footprint edge that blends into the neighbours' ground
GRADE = 5.0  # smoothing length of paved ground, metres
SEAM = 0.15  # paving meets a neighbour flush only when they are this close in height already
EDGE_RUN = (
    12  # edge samples (1 m apart) averaged each side, so the blended edge has no lumps either
)


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


def _sample(a, x, y, x0, y1, cell):
    """Bilinear sample of a grid whose row 0 is the north edge; cell centres carry the values."""
    fx = np.clip((x - x0) / cell - 0.5, 0, a.shape[1] - 1.001)
    fy = np.clip((y1 - y) / cell - 0.5, 0, a.shape[0] - 1.001)
    i, j = fx.astype(int), fy.astype(int)
    tx, ty = fx - i, fy - j
    top = a[j, i] * (1 - tx) + a[j, i + 1] * tx
    bottom = a[j + 1, i] * (1 - tx) + a[j + 1, i + 1] * tx
    return top * (1 - ty) + bottom * ty


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
        self, lidar_npz, edge=None, lifts=(), footprint=None, paved=(), voids=(), cell=1.0
    ):
        self.lifts, self.footprint = list(lifts), footprint
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
        base = _fill(np.where(n > 0, s / np.maximum(n, 1), np.nan))
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
            only = _masked_blur(base, mask.reshape(ny, nx), GRADE)
            self.graded = np.where(np.isfinite(only), only, self.graded)
        self.edge = None
        if edge:
            e = np.array(edge, float)
            if (
                EDGE_RUN > 0
            ):  # the samples run round the footprint: average along it, wrapping at the ends
                k = np.ones(2 * EDGE_RUN + 1) / (2 * EDGE_RUN + 1)
                ring = np.concatenate([e[-EDGE_RUN:, 2], e[:, 2], e[:EDGE_RUN, 2]])
                e[:, 2] = np.convolve(ring, k, mode="valid")
            self.edge = e

    def z(self, x, y, smooth=False):
        """Height before the edge blend: graded (`smooth`) or soft ground, plus the lifts."""
        x, y = np.asarray(x, float), np.asarray(y, float)
        a = self.graded if smooth else self.rough
        return _sample(a, x, y, self.x0, self.y1, self.cell) + self.lift(x, y)

    def surface(self, x, y, paved):
        """Finished height of points: `paved` (bool per point) picks graded ground; blended at the
        edge.
        """
        x, y = np.asarray(x, float), np.asarray(y, float)
        z = np.where(paved, self.z(x, y, True), self.z(x, y, False))
        if self.footprint is None or self.edge is None:
            return z
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
        """Height of the neighbours' ground at the nearest edge sample, NaN when there are none."""
        if self.edge is None or not len(self.edge):
            return np.full(np.shape(x), np.nan)
        out = np.empty(len(x))
        for k in range(0, len(x), 4096):  # in blocks, to bound the distance matrix
            d = (np.asarray(x)[k : k + 4096, None] - self.edge[None, :, 0]) ** 2 + (
                np.asarray(y)[k : k + 4096, None] - self.edge[None, :, 1]
            ) ** 2
            out[k : k + 4096] = self.edge[d.argmin(1), 2]
        return out

    def at(self, x, y):
        """Finished height of one point on paving (used to seat objects and curbs)."""
        return float(self.surface(np.array([x]), np.array([y]), np.array([True]))[0])
