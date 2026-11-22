"""Sample the ground the published tiles have along an area's footprint, so the new ground meets it
flush.

usage: python3 blender/scripted/edge.py AREA DUMP_DIR     (system Python with numpy)
DUMP_DIR is either a triangle dump of the published tiles (tiles.json and tiles.bin from
tools/evidence/dump_tiles.mjs ... --no-instances) of tiles supersede.mjs has cut: the top
of the other sources' ground meshes 5 cm outside the footprint, where it meets the new ground;
or (as the first areas were made)
ground_height.npy and ground.json from tools/evidence/plan.py --name ground, made from the tiles
BEFORE that: the median of the cells within 1.5 m, both sides of the outline. Writes
<area>/edge_heights.json: [x, y, z] every metre along the footprint (no sample where the tiles have
no ground). Run it again only when the footprint or the neighbouring models change.
"""

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geom  # noqa: E402
import layout  # noqa: E402
import terrain  # noqa: E402

# ground meshes of the other sources, by "mesh name material name" (README: edge_heights.json)
GROUND = re.compile(
    r"(?i)terrain|ground|skirt|farfield|lawn|asphalt|patch|apron|carriageway|walk|turf|fill"
    r"|platform|ballast|verge"
)
NOT_GROUND = re.compile(r"(?i)far_houses|crown|tree|roof|bleacher|field_lines|endzone|curb|wall")
# metres outside the footprint at which a triangle dump is read: tiles supersede.mjs cut end
# exactly on the outline (sw17), so the ground is read where it meets the new ground; 0.3 m (sw16)
# read the north model's terrain, which falls up to 1 m per metre from its cut edge, up to 0.25 m
# low
GAP = 0.05
REFINE_GAP = 0.05  # metres outside at which a step between two samples is looked for
REFINE = 0.05  # metres: how closely a step in the neighbour's ground is found between samples


def outside(ring, step=1.0, gap=GAP):
    """Points every `step` metres along a closed footprint, each with the point `gap` metres
    outside it along the outward normal: [(x, y, px, py), ...]."""
    pts = np.array([(p[0], p[1]) for p in geom.resample(list(ring), step, True)])
    n = terrain._normals([(p[0], p[1]) for p in ring], pts[:, 0], pts[:, 1])
    return [(x, y, x + gap * nx, y + gap * ny) for (x, y), (nx, ny) in zip(pts, n, strict=True)]


def top_z(tris, px, py):
    """Height of the highest triangle over each point (tris: n x 3 x 3), NaN where none is."""
    out = np.full(len(px), np.nan)
    lo, hi = tris[:, :, :2].min(1), tris[:, :, :2].max(1)
    for k, (x, y) in enumerate(zip(px, py, strict=True)):
        c = tris[(lo[:, 0] <= x) & (hi[:, 0] >= x) & (lo[:, 1] <= y) & (hi[:, 1] >= y)]
        if not len(c):
            continue
        a, b, q = c[:, 0], c[:, 1], c[:, 2]
        det = (b[:, 1] - q[:, 1]) * (a[:, 0] - q[:, 0]) + (q[:, 0] - b[:, 0]) * (a[:, 1] - q[:, 1])
        ok = np.abs(det) > 1e-12
        det = np.where(ok, det, 1.0)
        l1 = ((b[:, 1] - q[:, 1]) * (x - q[:, 0]) + (q[:, 0] - b[:, 0]) * (y - q[:, 1])) / det
        l2 = ((q[:, 1] - a[:, 1]) * (x - q[:, 0]) + (a[:, 0] - q[:, 0]) * (y - q[:, 1])) / det
        l3 = 1 - l1 - l2
        hit = ok & (np.minimum(np.minimum(l1, l2), l3) >= -1e-6)
        if hit.any():
            out[k] = (l1 * a[:, 2] + l2 * b[:, 2] + l3 * q[:, 2])[hit].max()
    return out


def sample(ring, tris, step=1.0, gap=GAP, tol=REFINE):
    """[x, y, z] along a closed footprint every `step` metres: the top of `tris` `gap` metres
    outside. Where two neighbouring samples differ by more than terrain.RUN_DZ (two meshes meet,
    a skirt and another model's sidewalk), the step between them is found by halving the run to
    `tol` metres, and a sample is added on either side of it, so the edge knows where the
    neighbour steps and not only that it does. A step found at a corner of the footprint takes,
    instead of the corner's own sample, one sample `tol` / 2 along each of its two edges: the
    ground then parts the two sides along the corner's bisector (terrain.Terrain.break_lines),
    not across one of the edges. No sample where the tiles have no ground."""
    ring = [(p[0], p[1]) for p in ring]
    pts = outside(ring, step, gap)
    z = top_z(tris, np.array([p[2] for p in pts]), np.array([p[3] for p in pts]))
    npts = len(pts)

    def at(x, y):  # read just outside the outline: where the two meshes meet at the outline
        n = terrain._normals(ring, np.array([x]), np.array([y]))[0]
        g = REFINE_GAP
        return float(top_z(tris, np.array([x + g * n[0]]), np.array([y + g * n[1]]))[0])

    def unit(i, j):
        (ax, ay), (bx, by) = pts[i][:2], pts[j][:2]
        ln = math.hypot(bx - ax, by - ay) or 1.0
        return (bx - ax) / ln, (by - ay) / ln

    def corner(i):
        (ux, uy), (vx, vy) = unit((i - 1) % npts, i), unit(i, (i + 1) % npts)
        return abs(ux * vy - uy * vx) > 0.02 or ux * vx + uy * vy < 0  # turns by over 1 degree

    def beside(i):
        """The two samples tol / 2 either side of corner i, before and after it."""
        (cx, cy), half = pts[i][:2], tol / 2
        (ux, uy), (vx, vy) = unit((i - 1) % npts, i), unit(i, (i + 1) % npts)
        out = []
        for px, py in ((cx - half * ux, cy - half * uy), (cx + half * vx, cy + half * vy)):
            zz = at(px, py)
            if np.isfinite(zz):
                out.append([round(px, 2), round(py, 2), round(zz, 3)])
        return out

    rows = {}  # sample index -> the samples that stand for it (a corner's are its two beside it)
    extra = {}  # sample index -> refined samples after it
    for k in range(npts):
        if np.isfinite(z[k]):
            rows.setdefault(k, [[round(pts[k][0], 2), round(pts[k][1], 2), round(float(z[k]), 3)]])
        j = (k + 1) % npts
        if not (np.isfinite(z[k]) and np.isfinite(z[j])) or abs(z[j] - z[k]) <= terrain.RUN_DZ:
            continue
        (ax, ay), (bx, by) = pts[k][:2], pts[j][:2]  # resample keeps corners: a straight run
        lo, hi, zlo, zhi = 0.0, 1.0, z[k], z[j]
        ln = math.hypot(bx - ax, by - ay)
        while (hi - lo) * ln > tol:
            mid = (lo + hi) / 2
            zm = at(ax + mid * (bx - ax), ay + mid * (by - ay))
            if not np.isfinite(zm):
                break
            if abs(zm - z[k]) <= abs(zm - z[j]):
                lo, zlo = mid, zm
            else:
                hi, zhi = mid, zm
        else:
            if lo == 0.0 and corner(k):
                rows[k] = beside(k)
            elif hi == 1.0 and corner(j):
                rows[j] = beside(j)
            else:
                extra[k] = [[round(ax + t * (bx - ax), 2), round(ay + t * (by - ay), 2),
                             round(float(zz), 3)] for t, zz in ((lo, zlo), (hi, zhi))
                            if 0.0 < t < 1.0]
    out = []
    for k in range(npts):
        out += rows.get(k, []) + extra.get(k, [])
    return out


def from_triangles(lay, dump):
    """Edge samples from a triangle dump: the other sources' ground (no scripted-build tile, no
    instanced mesh) GAP metres outside the footprint, at the footprint point."""
    meta = json.loads((dump / "tiles.json").read_text())["entries"]
    raw = np.fromfile(dump / "tiles.bin", np.float32).reshape(-1, 3, 3)
    keep = [
        raw[e["offset"] : e["offset"] + e["tris"]]
        for e in meta
        if not e["tile"].startswith("sw_")
        and not e["instanced"]
        and GROUND.search(e["mesh"] + " " + e["material"])
        and not NOT_GROUND.search(e["mesh"])
    ]
    tris = np.concatenate(keep).astype(float) if keep else np.zeros((0, 3, 3))
    return sample(lay["footprint"], tris)


def main():
    args = sys.argv[1:]
    plan_dir, dump = HERE / args[0], Path(args[1])
    lay = layout.load(plan_dir)
    if (dump / "tiles.json").exists():
        out = from_triangles(lay, dump)
        src = f"published tiles (models/main), ground meshes {GAP} m outside"
        json.dump(dict(source=src, samples=out), open(plan_dir / "edge_heights.json", "w"))
        print("edge samples", len(out))
        return
    meta = json.loads(Path(dump / "ground.json").read_text())
    h = np.load(dump / "ground_height.npy")
    x0, _y0, _x1, y1 = meta["box"]
    mpp = meta["mpp"]
    out = []
    for x, y, _s in geom.resample(lay["footprint"], 1.0, True):
        # median of the cells within 1.5 m: one raised curb or a tree base must not set the level
        i, j = math.floor((x - x0) / mpp), math.floor((y1 - y) / mpp)
        if not (0 <= i < h.shape[1] and 0 <= j < h.shape[0]):
            continue  # outside the raster: no sample here
        r = max(1, round(1.5 / mpp))
        win = h[max(0, j - r) : j + r + 1, max(0, i - r) : i + r + 1]
        if np.isfinite(win).any():
            out.append([round(x, 2), round(y, 2), round(float(np.nanmedian(win)), 3)])
    json.dump(
        dict(source="published tiles (models/main), ground meshes only", samples=out),
        open(plan_dir / "edge_heights.json", "w"),
    )
    print("edge samples", len(out))


if __name__ == "__main__":
    main()
