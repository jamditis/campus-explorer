"""LiDAR surface and ground grids for far-field building heights (used by landcover.py).

Reads USGS 3DEP point clouds over the +-2 km box and writes a 2 m grid in model metres:
  b   highest non-noise return per cell (surface)
  bl  highest last return per cell (canopy over a roof mostly passes through, so this sees the roof)
  b6  highest building (class 6) return per cell, where the dataset classifies buildings
  gs, gn  sum and count of ground (class 2) returns per cell
Sources: an Entwine (EPT) dataset URL, streamed node by node (e.g. the public usgs-lidar-public bucket),
or local .laz tiles. Nothing is kept but the grid.

usage: python ndsm_ept.py OUT.npz https://s3-us-west-2.amazonaws.com/usgs-lidar-public/NJ_NW6Co_2017
       python ndsm_ept.py OUT.npz https://s3-us-west-2.amazonaws.com/usgs-lidar-public/USGS_Lidar_Point_Cloud_NJ_SdL5_2014_LAS_2015
       CRS=EPSG:6347 python ndsm_ept.py OUT.npz tile1.laz ...   (CRS only needed when a tile has no WKT)
Run with a Python that has laspy[lazrs] and pyproj.
"""
import io
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import laspy
import numpy as np
from pyproj import CRS, Transformer

E0, N0, F = 575880.0, 738340.0, 1200 / 3937  # model origin (EPSG:6527 ftUS) and ftUS -> m
H, R = 2000, 2.0
NC = int(2 * H / R)
out, srcs = sys.argv[1], sys.argv[2:]
bmax = np.full((NC, NC), -1e9, "f4")
blast = np.full((NC, NC), -1e9, "f4")
b6 = np.full((NC, NC), -1e9, "f4")
gs = np.zeros((NC, NC), "f4")
gn = np.zeros((NC, NC), "f4")
tot = 0


def get(u):
    return urllib.request.urlopen(u, timeout=120).read()


def add(las, to_sp, zf):
    """Bin one point batch; to_sp maps its x, y to EPSG:6527 ftUS, zf converts its z to metres."""
    global tot
    cl = np.asarray(las.classification)
    m = (cl != 7) & (cl != 18) & (cl != 9)  # drop noise and water
    if not m.any():
        return
    e, n = to_sp(np.asarray(las.x)[m], np.asarray(las.y)[m])
    x, y = (e - E0) * F, (n - N0) * F
    z, c = np.asarray(las.z)[m] * zf, cl[m]
    last = (np.asarray(las.return_number) == np.asarray(las.number_of_returns))[m]
    col, row = ((x + H) / R).astype(int), ((H - y) / R).astype(int)
    ok = (col >= 0) & (col < NC) & (row >= 0) & (row < NC)
    col, row, z, c, last = col[ok], row[ok], z[ok].astype("f4"), c[ok], last[ok]
    np.maximum.at(bmax, (row, col), z)
    np.maximum.at(blast, (row[last], col[last]), z[last])
    k = c == 6
    np.maximum.at(b6, (row[k], col[k]), z[k])
    g = c == 2
    np.add.at(gs, (row[g], col[g]), z[g])
    np.add.at(gn, (row[g], col[g]), 1)
    tot += int(ok.sum())


def zfactor(crs):
    try:
        return crs.sub_crs_list[1].axis_info[0].unit_conversion_factor if crs.is_compound else crs.axis_info[0].unit_conversion_factor
    except Exception:
        return 1.0


for src in srcs:
    if src.startswith("http"):
        ept = json.loads(get(src + "/ept.json"))
        b = ept["bounds"]
        crs = CRS.from_user_input(ept["srs"].get("wkt") or "EPSG:" + ept["srs"]["horizontal"])
        to_sp = Transformer.from_crs(crs, 6527, always_xy=True).transform
        to_src = Transformer.from_crs(6527, crs, always_xy=True).transform
        cx, cy = to_src([E0 + dx / F for dx in (-H, H, -H, H)], [N0 + dy / F for dy in (-H, -H, H, H)])
        q = (min(cx) - 50, max(cx) + 50, min(cy) - 50, max(cy) + 50)
        nodes = []

        def walk(key, b=b, q=q, src=src, nodes=nodes):
            for k, n in json.loads(get(f"{src}/ept-hierarchy/{key}.json")).items():
                d, x, y, _z = map(int, k.split("-"))
                s = (b[3] - b[0]) / 2**d
                if b[0] + (x + 1) * s < q[0] or b[0] + x * s > q[1] or b[1] + (y + 1) * s < q[2] or b[1] + y * s > q[3]:
                    continue
                if n == -1:
                    walk(k)
                elif n > 0:
                    nodes.append(k)

        walk("0-0-0-0")
        print(src, "nodes", len(nodes), flush=True)
        with ThreadPoolExecutor(8) as ex:
            for las in ex.map(lambda k, src=src: laspy.read(io.BytesIO(get(f"{src}/ept-data/{k}.laz"))), nodes):
                add(las, to_sp, 1.0)
    else:
        with laspy.open(src) as f:
            crs = f.header.parse_crs() or CRS.from_user_input(os.environ["CRS"])  # older LAS 1.2 tiles: GeoTIFF keys only
            to_sp = Transformer.from_crs(crs, 6527, always_xy=True).transform
            zf = zfactor(crs)
            for chunk in f.chunk_iterator(3_000_000):
                add(chunk, to_sp, zf)
        print(src, "points so far", tot, flush=True)
np.savez_compressed(out, b=bmax, bl=blast, b6=b6, gs=gs, gn=gn)
print("saved", out, tot, "surface cells", int((bmax > -1e8).sum()), "last-return cells", int((blast > -1e8).sum()),
      "building cells", int((b6 > -1e8).sum()), "ground cells", int((gn > 0).sum()))
