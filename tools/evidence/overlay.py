"""Draw part of the fetched evidence with a metre grid, and plan files over it, to digitise and to
check.

usage: python tools/evidence/overlay.py OUT.png NAME X0 Y0 X1 Y1 [--zoom PX_PER_M] [--base
ortho|ndsm|hill|tiles|ground]
                                         [--grid METRES] [--plan FILE ...] [--labels]
NAME is the evidence folder under DATA (default /workspace/data) written by tools/evidence/fetch.py.
  ortho  the NJ 2020 aerial image
  ndsm   LiDAR height above ground: grey ground, yellow to red for 0.3 to 30 m (stands, poles,
  trees, roofs)
  hill   hillshade of the LiDAR ground with 0.25 m contours tinted (curbs, banks, cuttings)
  tiles  plan of what the published tiles hold there (tools/evidence/plan.py); ground = their ground
  only
Plan files use the format in blender/southwest/README.md. OUT.png must be outside the repository.
"""

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "blender" / "southwest"))
import geom  # noqa: E402

KIND = {
    "asphalt": (60, 160, 255),
    "concrete": (255, 255, 255),
    "brick": (255, 90, 60),
    "turf": (0, 255, 120),
    "lawn": (160, 255, 0),
    "mulch": (190, 120, 60),
    "ballast": (200, 200, 120),
    "gravel": (200, 200, 120),
}


def fill_nan(a):
    """
    Fill empty cells with the mean of their filled neighbours, pass after pass, until none are left.
    """
    a = a.copy()
    while np.isnan(a).any() and np.isfinite(a).any():
        p = np.pad(a, 1, constant_values=np.nan)
        stack = np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
        n = np.isfinite(stack).sum(0)
        mean = np.nansum(stack, 0) / np.maximum(n, 1)
        m = np.isnan(a) & (n > 0)
        a[m] = mean[m]
    return np.nan_to_num(a)


def base_image(kind, d, x0, y0, x1, y1, zoom):
    w, h = round((x1 - x0) * zoom), round((y1 - y0) * zoom)
    if kind in (
        "tiles",
        "ground",
    ):  # plan of the published tiles (tools/evidence/plan.py), all of it or ground only
        m = json.loads(
            Path(d / "tiles" / ("plan.json" if kind == "tiles" else "ground.json")).read_text()
        )
        im = Image.open(d / "tiles" / ("plan.png" if kind == "tiles" else "ground.png"))
        bx0, _, _, by1 = m["box"]
        box = (
            (x0 - bx0) / m["mpp"],
            (by1 - y1) / m["mpp"],
            (x1 - bx0) / m["mpp"],
            (by1 - y0) / m["mpp"],
        )
        return im.crop(tuple(round(v) for v in box)).resize((w, h), Image.NEAREST)
    if kind == "ortho":
        m = json.loads(Path(d / "ortho2020.json").read_text())
        im = Image.open(d / "ortho2020.png")
        box = (
            (x0 - m["x0"]) / m["mpp"],
            (m["y1"] - y1) / m["mpp"],
            (x1 - m["x0"]) / m["mpp"],
            (m["y1"] - y0) / m["mpp"],
        )
        return im.crop(tuple(round(v) for v in box)).resize((w, h), Image.LANCZOS)
    z = np.load(d / "lidar.npz")
    bx0, _by0, _bx1, by1, cell = z["box"]
    i0, i1 = int((x0 - bx0) / cell), int(math.ceil((x1 - bx0) / cell))
    j0, j1 = int((by1 - y1) / cell), int(math.ceil((by1 - y0) / cell))
    ground = fill_nan(z["ground"][j0:j1, i0:i1])
    if kind == "ndsm":
        hgt = np.nan_to_num(z["dsm"][j0:j1, i0:i1] - ground, nan=0.0)
        t = np.clip(np.log1p(np.maximum(hgt - 0.3, 0)) / math.log(31), 0, 1)
        rgb = np.stack(
            [
                90 + 165 * np.minimum(1, t * 3),
                90 + 165 * np.clip(1.5 - t * 2, 0, 1) * (t > 0),
                90 * (1 - np.minimum(1, t * 4)),
            ],
            -1,
        )
        rgb[hgt <= 0.3] = 90
    else:
        gy, gx = np.gradient(ground, cell)
        shade = np.clip(0.55 + 2.2 * (-gx * 0.6 + gy * 0.6), 0, 1)
        band = (np.floor(ground / 0.25) % 2) * 0.12
        rgb = np.stack([shade - band, shade, shade - band * 0.3], -1) * 255
    return Image.fromarray(np.clip(rgb, 0, 255).astype("u1")).resize((w, h), Image.BILINEAR)


def main():
    a = sys.argv[1:]
    opt = {"--zoom": "4", "--base": "ortho", "--grid": "10"}
    plans, labels, pos, i = [], False, [], 0
    while i < len(a):
        if a[i] == "--plan":
            i += 1
            while i < len(a) and not a[i].startswith("--"):
                plans.append(a[i])
                i += 1
            continue
        if a[i] == "--labels":
            labels = True
        elif a[i] in opt:
            opt[a[i]] = a[i + 1]
            i += 1
        else:
            pos.append(a[i])
        i += 1
    if len(pos) != 6:
        sys.exit(__doc__)
    out, name = Path(pos[0]).resolve(), pos[1]
    if REPO in out.parents:
        sys.exit("refusing to write evidence imagery inside the repository")
    x0, y0, x1, y1 = (float(v) for v in pos[2:])
    zoom, grid = float(opt["--zoom"]), float(opt["--grid"])
    d = Path(os.environ.get("DATA", "/workspace/data")) / name
    im = base_image(opt["--base"], d, x0, y0, x1, y1, zoom).convert("RGB")
    dr = ImageDraw.Draw(im)

    def px(p):
        return ((p[0] - x0) * zoom, (y1 - p[1]) * zoom)

    def poly(line, colour, closed, width=1):
        pts = [px(p) for p in line]
        dr.line(pts + pts[:1] if closed else pts, fill=colour, width=width)

    for f in plans:
        plan = json.loads(Path(f).read_text())
        if plan.get("footprint"):
            poly(geom.expand(plan["footprint"], True), (255, 0, 255), True, 2)
        for s in plan.get("surfaces", []):
            poly(geom.expand(s["ring"], True), KIND.get(s["kind"], (255, 255, 0)), True, 2)
            for hole in s.get("holes", []):
                poly(geom.expand(hole, True), KIND.get(s["kind"], (255, 255, 0)), True, 1)
            if labels:
                b = geom.bounds(geom.expand(s["ring"], True))
                dr.text(px(((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)), s["name"], fill=(255, 255, 0))
        for s in plan.get("strips", []):
            poly(geom.ribbon(s["centre"], s["width"]), KIND.get(s["kind"], (255, 255, 0)), True, 2)
        for c in plan.get("curbs", []):
            poly(
                geom.expand(c["path"], c.get("closed", False)),
                (255, 140, 0),
                c.get("closed", False),
                1,
            )
        for m in plan.get("markings", []):
            col = (
                (255, 255, 0)
                if m.get("colour") == "yellow"
                else (255, 60, 60)
                if m.get("colour") == "red"
                else (0, 255, 255)
            )
            if m["type"] == "line":
                poly(geom.expand(m["path"], m.get("closed", False)), col, m.get("closed", False), 1)
            elif m["type"] == "area":
                poly(geom.expand(m["ring"], True), col, True, 1)
            elif m["type"] == "stalls":
                for seg in geom.stalls(m):
                    poly(seg, col, False, 1)
        for p in plan.get("points", []):
            c = px(p["at"])
            dr.ellipse([c[0] - 4, c[1] - 4, c[0] + 4, c[1] + 4], outline=(255, 0, 255), width=2)
            if labels:
                dr.text((c[0] + 6, c[1] - 6), p.get("name", p["kind"]), fill=(255, 0, 255))
    if grid > 0:
        for gx in np.arange(math.ceil(x0 / grid) * grid, x1, grid):
            major = abs(gx / (grid * 5) - round(gx / (grid * 5))) < 1e-6
            dr.line(
                [px((gx, y0)), px((gx, y1))],
                fill=(255, 255, 0) if major else (150, 150, 60),
                width=1,
            )
            dr.text((px((gx, y1))[0] + 2, 2), f"{gx:g}", fill=(255, 255, 0))
        for gy in np.arange(math.ceil(y0 / grid) * grid, y1, grid):
            major = abs(gy / (grid * 5) - round(gy / (grid * 5))) < 1e-6
            dr.line(
                [px((x0, gy)), px((x1, gy))],
                fill=(255, 255, 0) if major else (150, 150, 60),
                width=1,
            )
            dr.text((2, px((x0, gy))[1] + 2), f"{gy:g}", fill=(255, 255, 0))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    print(out, im.size)


if __name__ == "__main__":
    main()
