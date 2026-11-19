"""Draw a plan (top view) of what the published tiles hold in a box, from a
tools/evidence/dump_tiles.mjs dump.

usage: python tools/evidence/plan.py DUMP_DIR [M_PER_PX] [--skip REGEX] [--only REGEX] [--name NAME]
Writes DUMP_DIR/NAME.png (top surface, flat material colours, lightly shaded),
DUMP_DIR/NAME_height.npy
(top surface height, NaN where empty), DUMP_DIR/NAME_id.npy (index into tiles.json entries, -1 where
empty)
and DUMP_DIR/NAME.json (box and metres per pixel), and prints the visible area of every mesh. NAME
defaults
to "plan". --skip and --only match "tile mesh material"; instanced meshes are left out with --only.
Row 0 is the north edge. The dump folder must be outside the repository.
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def raster(tri, w, h, x0, y1, mpp, top, ident, eid):
    """Z-buffer one entry's triangles (n, 3, 3) into the height and id grids: the top wins."""
    px = (tri[:, :, 0] - x0) / mpp
    py = (y1 - tri[:, :, 1]) / mpp
    z = tri[:, :, 2]
    for k in range(len(tri)):
        ax, bx, cx = px[k]
        ay, by, cy = py[k]
        i0, i1 = max(0, int(np.floor(min(ax, bx, cx)))), min(w - 1, int(np.ceil(max(ax, bx, cx))))
        j0, j1 = max(0, int(np.floor(min(ay, by, cy)))), min(h - 1, int(np.ceil(max(ay, by, cy))))
        if i1 < i0 or j1 < j0:
            continue
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(i0, i1 + 1) + 0.5, np.arange(j0, j1 + 1) + 0.5)
        l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l3 = 1 - l1 - l2
        zz = l1 * z[k, 0] + l2 * z[k, 1] + l3 * z[k, 2]
        sub_t, sub_i = top[j0 : j1 + 1, i0 : i1 + 1], ident[j0 : j1 + 1, i0 : i1 + 1]
        m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6) & (zz > sub_t)
        sub_t[m] = zz[m]
        sub_i[m] = eid


def main():
    d = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = {"--skip": None, "--only": None, "--name": "plan"}
    for k in opts:
        if k in sys.argv:
            opts[k] = sys.argv[sys.argv.index(k) + 1]
    args = [a for a in args if a not in opts.values()]
    skip = re.compile(opts["--skip"]) if opts["--skip"] else None
    only = re.compile(opts["--only"]) if opts["--only"] else None
    name = opts["--name"]
    mpp = float(args[0]) if args else 0.5
    meta = json.loads(Path(f"{d}/tiles.json").read_text())
    x0, y0, x1, y1 = meta["box"]
    tris = np.fromfile(f"{d}/tiles.bin", dtype="f4").reshape(-1, 3, 3)
    w, h = round((x1 - x0) / mpp), round((y1 - y0) / mpp)
    top = np.full((h, w), -1e9, "f4")
    ident = np.full((h, w), -1, "i4")
    for eid, e in enumerate(meta["entries"]):
        label = f"{e['tile']} {e['mesh']} {e['material']}"
        if (skip and skip.search(label)) or (only and (e["instanced"] or not only.search(label))):
            continue
        raster(tris[e["offset"] : e["offset"] + e["tris"]], w, h, x0, y1, mpp, top, ident, eid)
    col = np.array([e["color"][:3] for e in meta["entries"]] + [[0, 0, 0]], "f4") ** (1 / 2.2)
    img = col[ident]
    zs = np.where(top > -1e8, top, np.nan)
    gy, gx = np.gradient(np.nan_to_num(zs, nan=0.0), mpp)
    shade = np.clip(0.85 + 0.6 * (-gx * 0.5 + gy * 0.5), 0.45, 1.25)  # light from the north-west
    Image.fromarray((np.clip(img * shade[..., None], 0, 1) * 255).astype("u1")).save(
        f"{d}/{name}.png"
    )
    np.save(f"{d}/{name}_height.npy", zs)
    np.save(f"{d}/{name}_id.npy", ident)
    json.dump(dict(box=[x0, y0, x1, y1], mpp=mpp), open(f"{d}/{name}.json", "w"))
    ids, counts = np.unique(ident[ident >= 0], return_counts=True)
    for i, c in sorted(zip(ids, counts, strict=True), key=lambda t: -t[1])[:80]:
        e = meta["entries"][i]
        print(
            f"{c * mpp * mpp:9.0f} m2  {e['tile']:16s} {e['mesh'][:48]:48s} "
            f"{e['material'][:36]:36s} {e['cat']}"
        )


if __name__ == "__main__":
    main()
