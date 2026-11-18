"""Far-field land cover for the viewer, from OpenStreetMap (ODbL, credited in the viewer) and the
USGS 3DEP 10 m DEM the model's skirt is built from. No imagery is used.

Writes into OUT (models/main):
  landcover.webp   RGB land-cover colour map over the 4 km skirt (x, y in [-2000, 2000] Blender m)
  far_trees.bin    Float32 [x, y, z, crown radius, height] per tree (three.js axes), woods and yards
  far_houses.glb   (via RAW/far_houses.raw.glb + gltf-transform) real building footprints outside the modelled campus,
                   extruded with simple roofs: OSM where mapped, otherwise Microsoft Global ML Building Footprints (ODbL).
                   Heights come from USGS 3DEP LiDAR (surface minus ground) where it covers the footprint, then OSM
                   height/levels tags, then the footprint layer's own height estimate. Nothing is invented: where no
                   footprint exists the ground stays bare.
env: OSM (folder of .osm map tiles), DEM (skirt_dem_10m.npy), OUT, WORK_MAIN, WORK_NORTH (plans: what is modelled),
     FOOTPRINTS (Microsoft footprints clipped to the box, GeoJSON lines), NDSM (comma-separated LiDAR grids from ndsm_ept.py)
Run with a Python that has pyproj, shapely, numpy and Pillow.
"""
import glob
import json
import math
import os
import random
import re
import struct
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.strtree import STRtree

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
# modelled buildings and site features (same test make_chunks uses): no far-field footprint may double one
mbld = []
for wk in (WM, WN):
    p = wk + "/objects.json"
    if os.path.exists(p):
        for n, v in json.load(open(p)).items():
            x0, x1, y0, y1 = v["bb"][:4]
            if v["v"] and v["t"] == "MESH" and v.get("tri", 0) > 50 and max(x1 - x0, y1 - y0) < 150 and not n.startswith(("BD_", "MID_")) \
                    and not re.search(r"terrain|DTM|ground|apron|lawn|paving|asphalt|walk|curb|grass|tree|shrub|skirt|Context_", n, re.I):
                mbld.append((x0, x1, y0, y1))
mbld_a = np.array(mbld) if mbld else np.zeros((0, 4))


def in_modelled_building(x, y):
    a = mbld_a
    return bool(((a[:, 0] < x) & (x < a[:, 1]) & (a[:, 2] < y) & (y < a[:, 3])).any())


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
            buildings.append((pts, t))
# ---------- Microsoft Global ML Building Footprints (ODbL) where OSM has no building ----------
FOOTPRINTS = os.environ.get("FOOTPRINTS", "/workspace/nj-scenes/web/build/footprints/ms_bbox.geojsonl")
osm_polys = []
for pts, _t in buildings:
    p = Polygon(pts)
    osm_polys.append(p if p.is_valid else p.buffer(0))
osm_tree = STRtree(osm_polys) if osm_polys else None
n_ms = n_dup = 0
if os.path.exists(FOOTPRINTS):
    for line in open(FOOTPRINTS):
        f = json.loads(line)
        if f["geometry"]["type"] != "Polygon":
            continue
        ring = f["geometry"]["coordinates"][0]
        e, n = to_sp.transform([c[0] for c in ring], [c[1] for c in ring])
        pts = [((a - E0) * FT, (b - N0) * FT) for a, b in zip(e, n, strict=True)]
        p = Polygon(pts)
        if not p.is_valid or p.area < 12:
            continue
        if osm_tree is not None and any(p.intersection(osm_polys[i]).area > 0.3 * min(p.area, osm_polys[i].area) for i in osm_tree.query(p)):
            n_dup += 1  # OSM already maps this building
            continue
        h = f["properties"].get("height")
        t = {"building": "yes", "source": "microsoft"}
        if h and h > 0:
            t["ms_height"] = h
        dr.polygon([px(q) for q in pts], fill=PAL["building"])
        cd.polygon([px(q) for q in pts], fill=0)  # no far-field tree inside a building
        buildings.append((pts, t))
        n_ms += 1
print("microsoft footprints", n_ms, "skipped (already in OSM)", n_dup)
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


# ---------- LiDAR surface/ground grids (2 m, model metres; see ndsm_ept.py) ----------
NDSM = [g for g in os.environ.get("NDSM", "/workspace/nj-scenes/web/build/footprints/ndsm_b17.npz").split(",") if os.path.exists(g)]
LID = []
for g in NDSM:
    z = np.load(g)
    gn = z["gn"]
    LID.append((z["b"], np.where(gn > 0, z["gs"] / np.maximum(gn, 1), np.nan)))
LR, LH = 2.0, 2000.0
LN = int(2 * LH / LR)


def lidar_height(poly):
    """Building height from LiDAR: 75th percentile surface inside the footprint (shrunk 1 m off the eaves)
    minus the median ground in a 2-8 m ring around it. None when no grid covers it well."""
    inner = poly.buffer(-1.0)
    if inner.is_empty or inner.area < 8:
        inner = poly
    ring = poly.buffer(8).difference(poly.buffer(2))
    x0, y0, x1, y1 = ring.bounds
    c0, c1 = max(0, int((x0 + LH) / LR)), min(LN - 1, int((x1 + LH) / LR))
    r0, r1 = max(0, int((LH - y1) / LR)), min(LN - 1, int((LH - y0) / LR))
    if c1 < c0 or r1 < r0:
        return None
    cc, rr = np.meshgrid(np.arange(c0, c1 + 1), np.arange(r0, r1 + 1))
    xs, ys = -LH + (cc + 0.5) * LR, LH - (rr + 0.5) * LR
    from shapely import contains_xy
    m_in = contains_xy(inner, xs, ys)
    m_ring = contains_xy(ring, xs, ys)
    if m_in.sum() < 2:
        return None
    for surf, grd in LID:
        s_in = surf[r0:r1 + 1, c0:c1 + 1][m_in]
        g_r = grd[r0:r1 + 1, c0:c1 + 1][m_ring]
        s_in = s_in[s_in > -1e8]
        g_r = g_r[~np.isnan(g_r)]
        if len(s_in) >= max(2, 0.6 * m_in.sum()) and len(g_r) >= 4:
            h = float(np.percentile(s_in, 75) - np.median(g_r))
            if 2.0 <= h <= 60:
                return h
    return None


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
# two meshes by footprint source: OpenStreetMap and Microsoft Global ML Building Footprints
GEOM = {"far_houses_osm": ([], [], [], []), "far_houses_microsoft": ([], [], [], [])}
hsrc = {"lidar": 0, "osm tag": 0, "footprint estimate": 0, "default": 0}
P, NRM, COL, IDX = GEOM["far_houses_osm"]
WALL = [(0.62, 0.55, 0.46), (0.55, 0.50, 0.44), (0.66, 0.62, 0.55), (0.50, 0.38, 0.30), (0.58, 0.54, 0.47), (0.45, 0.47, 0.46)]
ROOF = [(0.20, 0.18, 0.17), (0.27, 0.22, 0.19), (0.17, 0.17, 0.18), (0.32, 0.24, 0.19), (0.24, 0.24, 0.23)]
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


# LiDAR height per building, and a scale for the footprint layer's own estimates (which run low here),
# fitted on the buildings that have both, so footprints outside LiDAR cover match those inside it
LHT = [lidar_height(Polygon(pts)) if Polygon(pts).is_valid else None for pts, _t in buildings]
pairs = [(lh, float(t["ms_height"])) for lh, (_p, t) in zip(LHT, buildings, strict=True) if lh and t.get("ms_height")]
MS_SCALE = float(np.median([a / b for a, b in pairs])) if len(pairs) > 50 else 1.0
print("lidar-covered footprints", sum(h is not None for h in LHT), "footprint-estimate scale", round(MS_SCALE, 3), "from", len(pairs))
for (pts, t), lh in zip(buildings, LHT, strict=True):
    P, NRM, COL, IDX = GEOM["far_houses_microsoft" if t.get("source") == "microsoft" else "far_houses_osm"]
    poly = Polygon(pts)
    if not poly.is_valid or poly.area < 12:
        continue
    cx, cy = poly.centroid.x, poly.centroid.y
    if abs(cx) > 1960 or abs(cy) > 1960 or is_modelled(cx, cy, 5) or in_modelled_building(cx, cy):
        continue
    h = lh
    if h is not None:
        hsrc["lidar"] += 1
    else:
        lv = t.get("building:levels")
        try:
            h = float(t["height"].split()[0]) if t.get("height") else (float(lv) * 3.1 + 1 if lv else None)
        except ValueError:
            h = None
        if h is not None:
            hsrc["osm tag"] += 1
        elif t.get("ms_height"):
            h = max(2.5, float(t["ms_height"]) * MS_SCALE)
            hsrc["footprint estimate"] += 1
        else:
            h = 7.5 if poly.area < 300 else 10  # footprint with no height anywhere: typical house / block
            hsrc["default"] += 1
    z0 = min(zat(x, y) for x, y in pts) - 0.3
    ring = list(poly.exterior.coords)[:-1]
    if Polygon(ring).exterior.is_ccw is False:
        ring = ring[::-1]
    wc = random.choice(WALL)
    rc = random.choice(ROOF)
    # h is roof-top height (LiDAR 90th percentile is near the ridge): small houses get a hip, so the eave sits below it
    small = poly.area < 350 and len(ring) <= 8
    rise = min(3.5, math.sqrt(poly.area) * 0.28, h * 0.35) if small else 0
    ztop = z0 + h - rise
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % len(ring)]
        a, b, c, d = (x1, z0, -y1), (x2, z0, -y2), (x2, ztop, -y2), (x1, ztop, -y1)
        add_tri(a, b, c, wc)
        add_tri(a, c, d, wc)
    # roof: small houses get a pyramid-ish hip (apex over the centroid), others stay flat
    apex = (cx, ztop + rise, -cy)
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % len(ring)]
        add_tri((x1, ztop, -y1), (x2, ztop, -y2), apex, rc)
    nb += 1


def write_glb(path):
    blobs, acc, meshes, nodes = [], [], [], []
    for name, (p_, n_, c_, i_) in GEOM.items():
        if not i_:
            continue
        pos = np.asarray(p_, np.float32)
        arrs = [(pos, "VEC3", 5126), (np.asarray(n_, np.float32), "VEC3", 5126), (np.asarray(c_, np.float32), "VEC3", 5126), (np.asarray(i_, np.uint32), "SCALAR", 5125)]
        base = len(acc)
        for k, (a_, typ, ct) in enumerate(arrs):
            blobs.append(a_.tobytes())
            d = {"bufferView": len(blobs) - 1, "componentType": ct, "count": len(a_), "type": typ}
            if k == 0:
                d["min"], d["max"] = pos.min(0).tolist(), pos.max(0).tolist()
            acc.append(d)
        meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": base, "NORMAL": base + 1, "COLOR_0": base + 2}, "indices": base + 3, "material": 0}]})
        nodes.append({"mesh": len(meshes) - 1, "name": name})
    offs, buf = [], b""
    for bl in blobs:
        offs.append(len(buf))
        buf += bl + b"\0" * ((4 - len(bl) % 4) % 4)
    g = {
        "asset": {"version": "2.0", "generator": "campus-explorer landcover.py"},
        "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}], "nodes": nodes,
        "materials": [{"name": "far_houses", "pbrMetallicRoughness": {"metallicFactor": 0, "roughnessFactor": 0.9}, "extras": {"cat": ""}}],
        "meshes": meshes,
        "buffers": [{"byteLength": len(buf)}],
        "bufferViews": [{"buffer": 0, "byteOffset": offs[i], "byteLength": len(blobs[i])} for i in range(len(blobs))],
        "accessors": acc,
    }
    js = json.dumps(g).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(buf)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(buf), 0x004E4942) + buf)


write_glb(RAW + "/far_houses.raw.glb")
print("far houses", nb, {k: len(v[3]) // 3 for k, v in GEOM.items()}, "heights from", hsrc)
