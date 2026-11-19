"""Fetch free public evidence for one part of the campus, in the model's local frame.

The model frame is metres east and north of E0, N0 in EPSG:6527 (see docs/VIEWER.md). Every output
goes to a data folder OUTSIDE the repository (DATA, default /workspace/data): imagery, rasters and
point clouds are never committed.

usage: python tools/evidence/fetch.py ortho NAME X0 Y0 X1 Y1 [M_PER_PX]   NJ 2020 natural colour
ortho (NJOGIS WMS)
       python tools/evidence/fetch.py lidar NAME X0 Y0 X1 Y1 [CELL_M]     USGS 3DEP point clouds
       (public EPT bucket)
       python tools/evidence/fetch.py osm   NAME X0 Y0 X1 Y1              OpenStreetMap (Overpass
       API, ODbL)

Outputs: DATA/NAME/ortho2020.png + ortho2020.json (bounds, metres per pixel),
         DATA/NAME/lidar.npz (points x, y, z, cls, ret, nret; grids dsm, last, ground on CELL_M
         cells),
         DATA/NAME/osm.json (elements with local x, y added to every node).
Needs pillow; lidar needs laspy[lazrs], numpy and pyproj; osm needs pyproj.
"""

import io
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

E0, N0, FT = 575880.0, 738340.0, 3937 / 1200  # model origin (EPSG:6527, ftUS) and metres -> ftUS
WMS = "https://img.nj.gov/imagerywms/Natural2020"
# 3DEP point clouds, newest first. The 2017 cloud ends near the station; the 2014 cloud covers the
# rest.
EPT = os.environ.get(
    "EPT",
    "https://s3-us-west-2.amazonaws.com/usgs-lidar-public/NJ_NW6Co_2017,"
    "https://s3-us-west-2.amazonaws.com/usgs-lidar-public/USGS_Lidar_Point_Cloud_NJ_SdL5_2014_LAS_2015",
).split(",")
OVERPASS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
)
OSM_API = "https://api.openstreetmap.org/api/0.6/map.json"
UA = {"User-Agent": "campus-model-evidence/1.0"}
REPO = Path(__file__).resolve().parents[2]


def get(url, data=None, tries=4):
    """GET (or POST when `data` is given) with a few retries; public servers drop requests now and
    then.
    """
    last = None
    for _ in range(tries):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(url, data=data, headers=UA), timeout=180
            ).read()
        except OSError as e:  # URLError and timeouts
            last = e
    raise last


def out_dir(name):
    d = Path(os.environ.get("DATA", "/workspace/data")).resolve() / name
    if REPO in d.parents or d == REPO:
        sys.exit(
            "refusing to write evidence inside the repository: set DATA to a folder outside it"
        )
    d.mkdir(parents=True, exist_ok=True)
    return d


def ortho(name, x0, y0, x1, y1, mpp=0.15):
    """Stitch WMS blocks into one image whose pixel (0, 0) is the north-west corner."""
    from PIL import Image

    w, h = round((x1 - x0) / mpp), round((y1 - y0) / mpp)
    img = Image.new("RGB", (w, h))
    step = 1800
    for j in range(0, h, step):
        for i in range(0, w, step):
            bw, bh = min(step, w - i), min(step, h - j)
            bx0, by1 = x0 + i * mpp, y1 - j * mpp
            box = (
                E0 + bx0 * FT,
                N0 + (by1 - bh * mpp) * FT,
                E0 + (bx0 + bw * mpp) * FT,
                N0 + by1 * FT,
            )
            q = urllib.parse.urlencode(
                dict(
                    SERVICE="WMS",
                    VERSION="1.1.1",
                    REQUEST="GetMap",
                    LAYERS="Natural2020",
                    STYLES="",
                    SRS="EPSG:6527",
                    BBOX=",".join(f"{v:.3f}" for v in box),
                    WIDTH=bw,
                    HEIGHT=bh,
                    FORMAT="image/png",
                )
            )
            img.paste(Image.open(io.BytesIO(get(f"{WMS}?{q}"))).convert("RGB"), (i, j))
    d = out_dir(name)
    img.save(d / "ortho2020.png")
    json.dump(
        dict(x0=x0, y0=y0, x1=x1, y1=y1, mpp=mpp, source=WMS), open(d / "ortho2020.json", "w")
    )
    print("ortho", d / "ortho2020.png", img.size)


def ept_points(src, x0, y0, x1, y1):
    """Points of one EPT dataset inside the box: columns x, y, z, class, return, returns (model
    metres).
    """
    import laspy
    import numpy as np
    from pyproj import CRS, Transformer

    ept = json.loads(get(src + "/ept.json"))
    b = ept["bounds"]
    crs = CRS.from_user_input(ept["srs"].get("wkt") or "EPSG:" + ept["srs"]["horizontal"])
    to_sp = Transformer.from_crs(crs, 6527, always_xy=True).transform
    to_src = Transformer.from_crs(6527, crs, always_xy=True).transform
    cx, cy = to_src(
        [E0 + x * FT for x in (x0, x1, x0, x1)], [N0 + y * FT for y in (y0, y0, y1, y1)]
    )
    q = (min(cx) - 5, max(cx) + 5, min(cy) - 5, max(cy) + 5)
    nodes = []

    def walk(key):
        for k, n in json.loads(get(f"{src}/ept-hierarchy/{key}.json")).items():
            depth, i, j, _ = map(int, k.split("-"))
            s = (b[3] - b[0]) / 2**depth
            if (
                b[0] + (i + 1) * s < q[0]
                or b[0] + i * s > q[1]
                or b[1] + (j + 1) * s < q[2]
                or b[1] + j * s > q[3]
            ):
                continue
            if n == -1:
                walk(k)
            elif n > 0:
                nodes.append(k)

    walk("0-0-0-0")
    parts = [np.zeros((0, 6), "f4")]
    with ThreadPoolExecutor(8) as ex:
        for las in ex.map(lambda k: laspy.read(io.BytesIO(get(f"{src}/ept-data/{k}.laz"))), nodes):
            e, n = to_sp(np.asarray(las.x), np.asarray(las.y))
            x, y = (e - E0) / FT, (n - N0) / FT
            m = (x >= x0) & (x < x1) & (y >= y0) & (y < y1)
            if m.any():
                parts.append(
                    np.stack(
                        [
                            x[m],
                            y[m],
                            np.asarray(las.z)[m],
                            np.asarray(las.classification)[m],
                            np.asarray(las.return_number)[m],
                            np.asarray(las.number_of_returns)[m],
                        ],
                        1,
                    )
                )
    return np.concatenate(parts).astype("f4")


def lidar(name, x0, y0, x1, y1, cell=0.5):
    """Stream the EPT nodes that touch the box; keep the points and three height grids.

    Each 10 m block takes its points from the first dataset (newest) that has ground returns there,
    so
    surveys of different years are not mixed inside one block. `pts` column 6 is the dataset index.
    """
    import numpy as np

    nx, ny = round((x1 - x0) / cell), round((y1 - y0) / cell)
    bx, by = math.ceil((x1 - x0) / 10), math.ceil((y1 - y0) / 10)
    taken = np.zeros((by, bx), bool)
    keep = []
    for si, src in enumerate(EPT):
        p = ept_points(src, x0, y0, x1, y1)
        bi = np.clip(((p[:, 0] - x0) / 10).astype(int), 0, bx - 1)
        bj = np.clip(((y1 - p[:, 1]) / 10).astype(int), 0, by - 1)
        has = np.zeros((by, bx), bool)
        has[bj[p[:, 3] == 2], bi[p[:, 3] == 2]] = True
        use = ~taken[bj, bi] & has[bj, bi]
        keep.append(np.column_stack([p[use], np.full(int(use.sum()), si, "f4")]))
        print(
            "lidar",
            src.rsplit("/", 1)[-1],
            len(p),
            "points in the box,",
            int(use.sum()),
            "kept,",
            int((has & ~taken).sum()),
            "blocks",
        )
        taken |= has
    p = np.concatenate(keep)
    x, y, z, c = p[:, 0], p[:, 1], p[:, 2], p[:, 3]
    col = np.clip(((x - x0) / cell).astype(int), 0, nx - 1)
    row = np.clip(
        ((y1 - y) / cell).astype(int), 0, ny - 1
    )  # row 0 is the north edge, like the ortho
    ok = (c != 7) & (c != 18)  # not noise
    dsm = np.full((ny, nx), np.nan, "f4")
    last = np.full((ny, nx), np.nan, "f4")
    np.fmax.at(dsm, (row[ok], col[ok]), z[ok])
    lr = ok & (p[:, 4] == p[:, 5])
    np.fmax.at(last, (row[lr], col[lr]), z[lr])
    g = c == 2
    gs, gn = np.zeros((ny, nx), "f4"), np.zeros((ny, nx), "f4")
    np.add.at(gs, (row[g], col[g]), z[g])
    np.add.at(gn, (row[g], col[g]), 1)
    ground = np.where(gn > 0, gs / np.maximum(gn, 1), np.nan).astype("f4")
    d = out_dir(name)
    np.savez_compressed(
        d / "lidar.npz",
        pts=p,
        dsm=dsm,
        last=last,
        ground=ground,
        box=np.array([x0, y0, x1, y1, cell]),
    )
    print(
        "lidar",
        d / "lidar.npz",
        len(p),
        "points,",
        f"{len(p) / ((x1 - x0) * (y1 - y0)):.1f} per m2, ground cells",
        f"{100 * float((gn > 0).mean()):.0f}%, blocks without ground",
        int((~taken).sum()),
    )


def osm(name, x0, y0, x1, y1):
    """Everything OpenStreetMap maps in the box, with each node's position in the model frame."""
    from pyproj import Transformer

    to_ll = Transformer.from_crs(6527, 4326, always_xy=True).transform
    to_sp = Transformer.from_crs(4326, 6527, always_xy=True).transform
    lon, lat = to_ll(
        [E0 + x * FT for x in (x0, x1, x0, x1)], [N0 + y * FT for y in (y0, y0, y1, y1)]
    )
    box = f"{min(lat)},{min(lon)},{max(lat)},{max(lon)}"
    query = (
        f"[out:json][timeout:90];(node({box});way({box});relation({box}););out body;>;out skel qt;"
    )
    body, data = urllib.parse.urlencode({"data": query}).encode(), None
    for server in OVERPASS:  # public Overpass servers are often busy: try the next one
        try:
            data = json.loads(get(server, data=body, tries=2))
            break
        except (OSError, ValueError) as e:
            print("overpass", server, "failed:", e)
    if data is None:  # the OpenStreetMap API serves the same elements for a small box
        data = json.loads(get(f"{OSM_API}?bbox={min(lon)},{min(lat)},{max(lon)},{max(lat)}"))
    for el in data["elements"]:
        if el["type"] == "node":
            e, n = to_sp(el["lon"], el["lat"])
            el["x"], el["y"] = round((e - E0) / FT, 3), round((n - N0) / FT, 3)
    d = out_dir(name)
    json.dump(data, open(d / "osm.json", "w"))
    print(
        "osm", d / "osm.json", len(data["elements"]), "elements (ODbL, OpenStreetMap contributors)"
    )


if __name__ == "__main__":
    if len(sys.argv) < 7 or sys.argv[1] not in ("ortho", "lidar", "osm"):
        sys.exit(__doc__)
    kind, name = sys.argv[1], sys.argv[2]
    nums = [float(v) for v in sys.argv[3:]]
    {"ortho": ortho, "lidar": lidar, "osm": osm}[kind](name, *nums)
