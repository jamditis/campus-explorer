"""Far-field land cover for the viewer, from OpenStreetMap (ODbL, credited in the viewer) and the
USGS 3DEP 10 m DEM the model's skirt is built from. No imagery is used.

Writes into OUT (models/main):
  landcover.webp   RGB land-cover colour map over the 4 km skirt (x, y in [-2000, 2000] Blender m)
  far_trees.bin    Float32 [x, y, z, crown radius, height] per tree (three.js axes), woods and yards
  far_houses.glb   (via RAW/far_houses.raw.glb + gltf-transform) OSM building footprints outside the modelled campus, extruded with simple roofs
env: OSM (folder of .osm map tiles), DEM (skirt_dem_10m.npy), OUT, WORK_MAIN, WORK_NORTH (plans: what is modelled)
Run with a Python that has pyproj, shapely, numpy and Pillow.
"""
import glob
import json
import math
import os
import random
import struct
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon

OSM = os.environ.get("OSM", "/workspace/nj-scenes/web/build/landcover")
DEM = os.environ.get("DEM", "/workspace/nj-scenes/montclair-state/data/skirt_dem_10m.npy")
OUT = os.environ.get("OUT", "models/main")
WM = os.environ.get("WORK_MAIN", "/workspace/nj-scenes/web/build/main")
WN = os.environ.get("WORK_NORTH", "/workspace/nj-scenes/web/build/north")
RAW = os.environ.get("RAW", WM)  # unoptimised houses GLB (build_web.sh compresses it into OUT)
E0, N0, FT = 575880.0, 738340.0, 1200 / 3937  # model origin (EPSG:6527 ftUS) and ftUS -> m
HALF, RES = 2000.0, 2048
random.seed(7)
to_sp = Transformer.from_crs("EPSG:4326", "EPSG:6527", always_xy=True)

# ---------- OSM ----------
nodes, ways, rels = {}, {}, []
for f in sorted(glob.glob(OSM + "/*.osm")):
    for el in ET.parse(f).getroot():
        if el.tag == "node":
            nodes[el.get("id")] = (float(el.get("lon")), float(el.get("lat")))
        elif el.tag == "way":
            ways[el.get("id")] = ([n.get("ref") for n in el.findall("nd")], {t.get("k"): t.get("v") for t in el.findall("tag")})
        elif el.tag == "relation":
            rels.append(([(m.get("ref"), m.get("role")) for m in el.findall("member") if m.get("type") == "way"], {t.get("k"): t.get("v") for t in el.findall("tag")}))
ids = list(nodes)
lon = np.array([nodes[i][0] for i in ids])
lat = np.array([nodes[i][1] for i in ids])
E, N = to_sp.transform(lon, lat)
local = {i: ((e - E0) * FT, (n - N0) * FT) for i, e, n in zip(ids, E, N, strict=True)}
print("osm nodes", len(nodes), "ways", len(ways), "relations", len(rels))


def coords(refs):
    return [local[r] for r in refs if r in local]


# ---------- what the model already covers (no far-field trees or houses there) ----------
modelled = []
for wk in (WM, WN):
    p = wk + "/objects.json"
    if not os.path.exists(p):
        continue
    for n, v in json.load(open(p)).items():
        x0, x1, y0, y1 = v["bb"][:4]
        if v["v"] and v["t"] == "MESH" and ("terrain" in n.lower() or "DTM" in n) and 100 < max(x1 - x0, y1 - y0) < 1500:
            modelled.append((x0, x1, y0, y1))
print("modelled terrain boxes", modelled)


def is_modelled(x, y, pad=0.0):
    return any(x0 - pad < x < x1 + pad and y0 - pad < y < y1 + pad for x0, x1, y0, y1 in modelled)


# ---------- land-cover colour map ----------
PAL = {
    "base": (88, 104, 62), "wood": (44, 60, 34), "scrub": (70, 84, 48), "grass": (98, 122, 64),
    "park": (92, 118, 60), "golf": (104, 134, 70), "residential": (84, 98, 62), "commercial": (118, 116, 110),
    "industrial": (112, 110, 104), "parking": (104, 104, 104), "water": (58, 78, 92), "rail": (92, 84, 76),
    "road": (82, 82, 86), "building": (122, 116, 108), "cemetery": (90, 112, 64),
}


def classify(t):
    lu, na, le = t.get("landuse"), t.get("natural"), t.get("leisure")
    if na in ("wood",) or lu == "forest":
        return "wood"
    if na in ("scrub", "heath", "wetland"):
        return "scrub"
    if na == "water" or lu in ("reservoir", "basin") or t.get("water"):
        return "water"
    if le == "golf_course":
        return "golf"
    if le in ("park", "pitch", "playground", "garden", "recreation_ground", "nature_reserve") or lu in ("recreation_ground", "village_green"):
        return "park"
    if lu in ("grass", "meadow", "farmland"):
        return "grass"
    if lu == "cemetery":
        return "cemetery"
    if lu == "residential":
        return "residential"
    if lu in ("commercial", "retail"):
        return "commercial"
    if lu in ("industrial", "railway"):
        return "industrial"
    if t.get("amenity") == "parking":
        return "parking"
    return None


img = Image.new("RGB", (RES, RES), PAL["base"])
dr = ImageDraw.Draw(img)
cls_img = Image.new("L", (RES, RES), 0)
cd = ImageDraw.Draw(cls_img)
blk = Image.new("L", (RES, RES), 0)  # 255 = no synthetic house here (roads, buildings, water, woods, parks)
bd = ImageDraw.Draw(blk)
CLS = {"wood": 1, "residential": 2, "park": 3, "scrub": 4, "cemetery": 5, "golf": 6}
px = lambda p: ((p[0] + HALF) / (2 * HALF) * RES, (HALF - p[1]) / (2 * HALF) * RES)
areas = []
for refs, t in ways.values():
    c = classify(t)
    if c and len(refs) > 3 and refs[0] == refs[-1]:
        pts = coords(refs)
        if len(pts) > 3:
            areas.append((Polygon(pts).area, c, pts))
for mem, t in rels:
    c = classify(t)
    if not c:
        continue
    for ref, role in mem:
        if role == "outer" and ref in ways:
            pts = coords(ways[ref][0])
            if len(pts) > 3:
                areas.append((Polygon(pts).area, c, pts))
# big areas first so smaller ones (parks inside residential) paint on top
ORDER = ["residential", "commercial", "industrial", "cemetery", "golf", "grass", "park", "scrub", "wood", "parking", "water"]
for _, kind, pts in sorted(areas, key=lambda a: (-a[0], ORDER.index(a[1]) if a[1] in ORDER else 0)):
    dr.polygon([px(p) for p in pts], fill=PAL[kind])
    cd.polygon([px(p) for p in pts], fill=CLS.get(kind, 0))
    bd.polygon([px(p) for p in pts], fill=0 if kind == "residential" else 255)
ROADW = {"motorway": 14, "trunk": 12, "primary": 11, "secondary": 9, "tertiary": 8, "residential": 6.5, "unclassified": 6, "service": 4, "living_street": 5}
for refs, t in ways.values():
    h = t.get("highway")
    pts = coords(refs)
    if len(pts) < 2:
        continue
    if h in ROADW:
        w = max(1, int(round(ROADW[h] / (2 * HALF / RES))))
        dr.line([px(p) for p in pts], fill=PAL["road"], width=w)
        cd.line([px(p) for p in pts], fill=0, width=w + 2)
        bd.line([px(p) for p in pts], fill=255, width=w + 3)
    elif t.get("railway") in ("rail", "light_rail"):
        dr.line([px(p) for p in pts], fill=PAL["rail"], width=max(1, int(6 / (2 * HALF / RES))))
        cd.line([px(p) for p in pts], fill=0, width=4)
buildings = []
for refs, t in ways.values():
    if "building" in t and len(refs) > 3 and refs[0] == refs[-1]:
        pts = coords(refs)
        if len(pts) > 3:
            dr.polygon([px(p) for p in pts], fill=PAL["building"])
            cd.polygon([px(p) for p in pts], fill=0)
            bd.polygon([px(p) for p in pts], fill=255)
            buildings.append((pts, t))
# ---------- synthetic frontage houses (OSM has few house footprints here) ----------
# Along residential streets outside the modelled campus: a 9-11 x 11-14 m house every ~22 m on both
# sides, set back from the road, only on residential or untagged land that is free of roads, mapped
# buildings, water, woods and parks. These are placeholders for the far field, not mapped buildings.
SYN = {"residential", "unclassified", "living_street", "tertiary"}
blk_a = np.asarray(blk)
taken = set()
synth = []


def free(x, y, r=4.5):
    for dx in (-r, 0, r):
        for dy in (-r, 0, r):
            u, v = px((x + dx, y + dy))
            if not (0 <= u < RES and 0 <= v < RES) or blk_a[int(v), int(u)]:
                return False
    return True


for refs, t in ways.values():
    if t.get("highway") not in SYN:
        continue
    pts = coords(refs)
    off = ROADW.get(t.get("highway"), 6) / 2 + 12
    for (x1, y1), (x2, y2) in zip(pts, pts[1:], strict=False):
        L = math.hypot(x2 - x1, y2 - y1)
        if L < 8:
            continue
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        s0 = random.uniform(4, 14)
        while s0 < L - 4:
            for side in (-1, 1):
                cx = x1 + ux * s0 - uy * off * side
                cy = y1 + uy * s0 + ux * off * side
                key = (int(cx // 16), int(cy // 16))
                if key in taken or abs(cx) > 1950 or abs(cy) > 1950 or is_modelled(cx, cy, 15) or not free(cx, cy):
                    continue
                taken.add(key)
                w, d = random.uniform(9, 11) / 2, random.uniform(11, 14) / 2
                corners = [(cx + ux * a - uy * b * side, cy + uy * a + ux * b * side) for a, b in ((-w, -d), (w, -d), (w, d), (-w, d))]
                synth.append(corners)
                dr.polygon([px(p) for p in corners], fill=PAL["building"])
            s0 += random.uniform(19, 26)
print("synthetic houses", len(synth))
for c in synth:
    buildings.append((c + [c[0]], {"building": "house", "synthetic": "yes"}))
# light per-pixel variation so flat fills don't read as paint
a = np.asarray(img).astype(np.float32)
noise = np.random.default_rng(3).normal(0, 1, (RES // 8, RES // 8)).astype(np.float32)
noise = np.asarray(Image.fromarray(noise).resize((RES, RES), Image.BICUBIC))
a *= (1 + 0.06 * noise)[..., None]
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(OUT + "/landcover.webp", quality=82, method=6)
print("landcover.webp", os.path.getsize(OUT + "/landcover.webp"))

# ---------- heights ----------
D = np.load(DEM)


def zat(x, y):
    c = (x + 2000) / 10 - 0.5
    r = (2000 - y) / 10 - 0.5
    c0, r0 = int(np.clip(math.floor(c), 0, 398)), int(np.clip(math.floor(r), 0, 398))
    fc, fr = min(max(c - c0, 0), 1), min(max(r - r0, 0), 1)
    return float(D[r0, c0] * (1 - fc) * (1 - fr) + D[r0, c0 + 1] * fc * (1 - fr) + D[r0 + 1, c0] * (1 - fc) * fr + D[r0 + 1, c0 + 1] * fc * fr)


# ---------- far trees: woods dense, yards and parks sparse ----------
cls = np.asarray(cls_img)
DENS = {1: 1 / 70, 4: 1 / 160, 2: 1 / 320, 5: 1 / 250, 3: 1 / 500, 6: 1 / 900}
pxa = (2 * HALF / RES) ** 2
trees = []
for k, dens in DENS.items():
    ys, xs = np.nonzero(cls == k)
    n = int(len(xs) * pxa * dens)
    if not n:
        continue
    pick = np.random.default_rng(k).choice(len(xs), size=min(n, len(xs)), replace=False)
    for i in pick:
        x = (xs[i] + random.random()) / RES * 2 * HALF - HALF
        y = HALF - (ys[i] + random.random()) / RES * 2 * HALF
        if abs(x) > 1960 or abs(y) > 1960 or is_modelled(x, y, 10):
            continue
        h = random.uniform(10, 20) if k == 1 else random.uniform(7, 15)
        trees.append((x, zat(x, y) - 0.5, -y, h * random.uniform(0.22, 0.32), h))
trees = trees[:40000]
with open(OUT + "/far_trees.bin", "wb") as f:
    f.write(np.asarray(trees, np.float32).tobytes())
print("far trees", len(trees))

# ---------- far houses: extruded OSM footprints with a low hip/flat roof ----------
P, NRM, COL, IDX = [], [], [], []
WALL = [(0.78, 0.74, 0.68), (0.70, 0.66, 0.60), (0.82, 0.80, 0.76), (0.62, 0.52, 0.44), (0.74, 0.70, 0.62)]
ROOF = [(0.30, 0.29, 0.29), (0.36, 0.32, 0.30), (0.26, 0.26, 0.28), (0.42, 0.36, 0.32)]
nb = 0


def add_tri(a, b, c, col):
    n = np.cross(np.subtract(b, a), np.subtract(c, a))
    ln = np.linalg.norm(n) or 1
    n = n / ln
    base = len(P)
    for v in (a, b, c):
        P.append(v)
        NRM.append(n)
        COL.append(col)
    IDX.extend((base, base + 1, base + 2))


for pts, t in buildings:
    poly = Polygon(pts)
    if not poly.is_valid or poly.area < 12:
        continue
    cx, cy = poly.centroid.x, poly.centroid.y
    if abs(cx) > 1960 or abs(cy) > 1960 or is_modelled(cx, cy, 5):
        continue
    lv = t.get("building:levels")
    try:
        h = float(t.get("height", "").split()[0]) if t.get("height") else (float(lv) * 3.1 + 1 if lv else (7.5 if poly.area < 300 else 10))
    except ValueError:
        h = 7.5
    z0 = min(zat(x, y) for x, y in pts) - 0.3
    ring = list(poly.exterior.coords)[:-1]
    if Polygon(ring).exterior.is_ccw is False:
        ring = ring[::-1]
    wc = random.choice(WALL)
    rc = random.choice(ROOF)
    ztop = z0 + h
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % len(ring)]
        a, b, c, d = (x1, z0, -y1), (x2, z0, -y2), (x2, ztop, -y2), (x1, ztop, -y1)
        add_tri(a, b, c, wc)
        add_tri(a, c, d, wc)
    # roof: small houses get a pyramid-ish hip (apex over the centroid), others stay flat
    small = poly.area < 350 and len(ring) <= 8
    apex = (cx, ztop + (min(3.5, math.sqrt(poly.area) * 0.28) if small else 0), -cy)
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % len(ring)]
        add_tri((x1, ztop, -y1), (x2, ztop, -y2), apex, rc)
    nb += 1


def write_glb(path):
    pos = np.asarray(P, np.float32)
    nrm = np.asarray(NRM, np.float32)
    col = np.asarray(COL, np.float32)
    idx = np.asarray(IDX, np.uint32)
    blobs = [pos.tobytes(), nrm.tobytes(), col.tobytes(), idx.tobytes()]
    offs, buf = [], b""
    for bl in blobs:
        offs.append(len(buf))
        buf += bl + b"\0" * ((4 - len(bl) % 4) % 4)
    g = {
        "asset": {"version": "2.0", "generator": "campus-explorer landcover.py"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": "far_houses_osm"}],
        "materials": [{"name": "far_houses", "pbrMetallicRoughness": {"metallicFactor": 0, "roughnessFactor": 0.9}, "extras": {"cat": ""}}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "COLOR_0": 2}, "indices": 3, "material": 0}]}],
        "buffers": [{"byteLength": len(buf)}],
        "bufferViews": [{"buffer": 0, "byteOffset": offs[i], "byteLength": len(blobs[i])} for i in range(4)],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(pos), "type": "VEC3", "min": pos.min(0).tolist(), "max": pos.max(0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": len(nrm), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(col), "type": "VEC3"},
            {"bufferView": 3, "componentType": 5125, "count": len(idx), "type": "SCALAR"},
        ],
    }
    js = json.dumps(g).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(buf)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(buf), 0x004E4942) + buf)


write_glb(RAW + "/far_houses.raw.glb")
print("far houses", nb, "tris", len(IDX) // 3)
