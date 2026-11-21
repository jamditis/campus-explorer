"""Sample the ground the published tiles have along an area's footprint, so the new ground meets it
flush.

usage: python3 blender/scripted/edge.py AREA DUMP_DIR     (system Python with numpy)
DUMP_DIR is either a triangle dump of the published tiles (tiles.json and tiles.bin from
tools/evidence/dump_tiles.mjs ... --no-instances): the top of the other sources' ground meshes
0.3 m outside the footprint, where it is the ground the new ground meets, the same before and
after the scripted build superseded the ground inside; or (as the first areas were made)
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
GAP = 0.3  # metres outside the footprint at which a triangle dump is read


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
    pts = outside(lay["footprint"])
    z = top_z(tris, np.array([p[2] for p in pts]), np.array([p[3] for p in pts]))
    return [
        [round(x, 2), round(y, 2), round(float(h), 3)]
        for (x, y, _px, _py), h in zip(pts, z, strict=True)
        if np.isfinite(h)
    ]


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
