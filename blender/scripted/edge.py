"""Sample the ground the published tiles have along an area's footprint, so the new ground meets it
flush.

usage: python3 blender/scripted/edge.py AREA DUMP_DIR     (system Python with numpy)
DUMP_DIR holds ground_height.npy and ground.json from tools/evidence/plan.py --name ground, made
from the tiles BEFORE the scripted build superseded their ground there. Writes
<area>/edge_heights.json: [x, y, z] every metre along the footprint (no sample where the tiles have
no ground). Run it again only when the footprint or the neighbouring models change.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geom  # noqa: E402
import layout  # noqa: E402


def main():
    args = sys.argv[1:]
    plan_dir, dump = HERE / args[0], Path(args[1])
    lay = layout.load(plan_dir)
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
