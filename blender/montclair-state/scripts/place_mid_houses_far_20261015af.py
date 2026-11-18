"""2026-10-15 ~1:24 AM ET, tag 20261015af. RERUNNABLE. --save to write.
Port of place_mid_houses_mid_20261015ae.py to houses_scatter_20261014z FAR band 3.5-6 km ESE
(400 OSM ways not in ad+ae; geometry from data/ccom_mid_distance/af/house_footprints_far_20261015af.json,
public OSM API 0.6, (c) OSM contributors, EPSG:6527 via pyproj, same origin).
Reuses protos MID_house_protos_20261014ad (rebuilt roofs, shared meshes). No re-append.
Farther half (dist_m >= 4750): lower LOD — no Flat_Apartments_Low; map apartments/commercial to hip/gable.
Footprint position/orientation/size: ACCURATE-to-OSM. Form/height/roof/colour: UNVERIFIED. No lamps / no street furniture.
"""
import bpy, json, math, os, sys, random
from mathutils import Vector

SAVE = "--save" in sys.argv
TAG = "20261015af"
PTAG = "20261014ad"  # proto tag
ROOT = bpy.path.abspath("//")
JSON = os.path.join(ROOT, "data", "ccom_mid_distance", "af", "house_footprints_far_20261015af.json")
COL_NAME = f"MID_houses_far_{TAG}"
PROTO_COL = f"MID_house_protos_{PTAG}"
TYPES = {
    "House_Gable_Tan_1storey": (10.0, 8.0, 5.0),
    "House_Gable_Grey_2storey": (11.0, 9.0, 8.0),
    "House_Hip_Brick_2storey": (12.0, 10.0, 8.0),
    "House_Duplex_Tan": (14.0, 8.0, 7.0),
    "House_Flat_Apartments_Low": (18.0, 12.0, 11.0),
}
LOD_FAR_M = 4750.0  # farther half: skip flat-apartment proto
rng = random.Random(2026101500)
sc = bpy.context.scene
SKY_CAM = Vector((26.975, -13.051, 140.617))
EXCLUDE = [
    {"name": "CCOM", "xmin": -30, "xmax": 55, "ymin": -45, "ymax": 35},
    {"name": "Morehead", "xmin": -90, "xmax": -20, "ymin": -80, "ymax": 20},
    {"name": "LifeHall", "xmin": -120, "xmax": -40, "ymin": 40, "ymax": 160},
]
GROUND = ["Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho", "Context_ground_beyond_data", "Terrain_LiDAR_DTM_1m"]

proto_parent = bpy.data.collections.get(PROTO_COL)
if proto_parent is None:
    raise SystemExit("protos missing: run ad first")

def find_lc(lc, name):
    if lc.collection.name == name:
        return lc
    for ch in lc.children:
        r = find_lc(ch, name)
        if r:
            return r
lc = find_lc(bpy.context.view_layer.layer_collection, PROTO_COL)
if lc:
    lc.exclude = True

gobs = [bpy.data.objects[n] for n in GROUND if n in bpy.data.objects]
def ground_z(x, y):
    best = None
    for o in gobs:
        mi = o.matrix_world.inverted()
        orig = mi @ Vector((x, y, 3000.0))
        d = (mi.to_3x3() @ Vector((0, 0, -1))).normalized()
        ok, loc, nor, idx = o.ray_cast(orig, d)
        if ok:
            z = (o.matrix_world @ loc).z
            best = z if best is None else max(best, z)
    return best

def in_exclude(x, y):
    for e in EXCLUDE:
        if e["xmin"] - 20 <= x <= e["xmax"] + 20 and e["ymin"] - 20 <= y <= e["ymax"] + 20:
            return e["name"]

def pick(b, low_lod):
    tag = (b.get("building_tag") or "yes").lower()
    A = b["area_m2"]; L, S = b["mrr_long_m"], b["mrr_short_m"]
    lv = None
    try:
        lv = float(b.get("levels")) if b.get("levels") else None
    except ValueError:
        lv = None
    if tag == "roof":
        return None, None, "skip_roof_canopy"
    if tag in ("garage", "shed") or A < 70:
        return "House_Gable_Tan_1storey", 3.2, "garage_small"
    if low_lod:
        # far LOD: no Flat_Apartments; apartments/commercial -> hip/gable boxes
        if tag in ("retail", "commercial", "industrial", "warehouse", "apartments") or A > 700:
            h = (lv * 3.0 + 1.0) if lv else rng.uniform(5.5, 8.5)
            h = min(h, 9.0)  # cap tall poke into skyline
            return "House_Hip_Brick_2storey", h, "far_lod_block"
        if tag in ("terrace", "semidetached_house") or (L / max(S, 1) > 1.7 and 160 < A < 450):
            return "House_Duplex_Tan", rng.uniform(6.0, 7.2), "duplex"
        if A < 130:
            return "House_Gable_Tan_1storey", None, "house_small"
        return rng.choice(["House_Gable_Grey_2storey", "House_Hip_Brick_2storey"]), None, "house"
    # near-far half: same picker as ae
    if tag in ("retail", "commercial", "industrial", "warehouse"):
        return "House_Flat_Apartments_Low", (lv * 4.0 + 1.0) if lv else rng.uniform(4.8, 6.0), "commercial_flat"
    if tag == "apartments" or A > 700:
        h = (lv * 3.0 + 1.2) if lv else (rng.choice([7.5, 10.5, 11.4]) if A < 1500 else 11.4)
        if tag == "yes" and lv:
            h = lv * 4.0 + 0.8
        return "House_Flat_Apartments_Low", h, "apartments_flat"
    if tag in ("terrace", "semidetached_house") or (L / max(S, 1) > 1.7 and 160 < A < 450):
        return "House_Duplex_Tan", rng.uniform(6.6, 7.6), "duplex"
    if A < 130:
        return rng.choice(["House_Gable_Tan_1storey", "House_Gable_Grey_2storey"]), None, "house_small"
    if A < 450:
        return rng.choice(["House_Gable_Grey_2storey", "House_Hip_Brick_2storey", "House_Gable_Grey_2storey"]), None, "house"
    return rng.choice(["House_Flat_Apartments_Low", "House_Hip_Brick_2storey"]), None, "large_res"

col = bpy.data.collections.get(COL_NAME)
if col is None:
    col = bpy.data.collections.new(COL_NAME)
    sc.collection.children.link(col)
for o in list(col.objects):
    bpy.data.objects.remove(o, do_unlink=True)
col["TAG"] = TAG
col["UNVERIFIED"] = "OSM footprint position/orientation/size ACCURATE-to-OSM; house form/height/roof/colour UNVERIFIED proxies; far half LOD reduced (no flat-apt proto)"

canopy = bpy.data.collections.get("MID_canopy_near_20261014ac")
crowns = [o for o in canopy.objects if o.type == "MESH"] if canopy else []
for o in crowns:
    if o.get("hidden_by") == TAG:
        o.hide_render = False; o.hide_viewport = False; del o["hidden_by"]

data = json.load(open(JSON))["buildings"]
stats = {"placed": 0, "skip": {}, "kinds": {}, "crowns_hidden": 0, "sightline_flag": 0, "low_lod": 0}
SKY_BASE_ANG = math.degrees(math.atan2(0.0 - SKY_CAM.z, 21700.0))
for b in data:
    if not b.get("centroid_local_m"):
        stats["skip"]["no_geom"] = stats["skip"].get("no_geom", 0) + 1; continue
    cx, cy = b["centroid_local_m"]
    if in_exclude(cx, cy):
        stats["skip"]["campus"] = stats["skip"].get("campus", 0) + 1; continue
    dist_m = b.get("z_dist_m") or math.hypot(cx - SKY_CAM.x, cy - SKY_CAM.y)
    low_lod = dist_m >= LOD_FAR_M
    tname, height, kind = pick(b, low_lod)
    if tname is None:
        stats["skip"][kind] = stats["skip"].get(kind, 0) + 1; continue
    src = bpy.data.collections.get(tname + "_" + PTAG)
    if src is None:
        stats["skip"]["no_proto"] = stats["skip"].get("no_proto", 0) + 1; continue
    bx, by, bh = TYPES[tname]
    L, S = b["mrr_long_m"], b["mrr_short_m"]
    sx = max(0.35, min(6.0, L / bx)); sy = max(0.35, min(6.0, S / by))
    if height:
        sz = height / bh
    else:
        sz = max(0.85, min(1.2, math.sqrt(sx * sy))) * rng.uniform(0.95, 1.05)
    if low_lod:
        sz = min(sz, 1.05)  # keep far LOD short
        stats["low_lod"] += 1
    zs = [ground_z(x, y) for x, y in b["footprint_local_m"][::max(1, len(b["footprint_local_m"]) // 8)]] + [ground_z(cx, cy)]
    zs = [z for z in zs if z is not None]
    if not zs:
        stats["skip"]["no_ground"] = stats["skip"].get("no_ground", 0) + 1; continue
    z0 = min(zs) - 0.35
    slope = max(zs) - min(zs)
    yaw = b["yaw_long_axis_rad"] + (math.pi if rng.random() < 0.5 else 0.0)
    dx, dy = cx - SKY_CAM.x, cy - SKY_CAM.y
    dist = math.hypot(dx, dy); bear = math.degrees(math.atan2(dy, dx))
    top = z0 + bh * sz + 1.0
    ang = math.degrees(math.atan2(top - SKY_CAM.z, dist))
    if -40 <= bear <= -25 and ang > SKY_BASE_ANG:
        stats["sightline_flag"] += 1
        sz = max(0.3, ((SKY_CAM.z + math.tan(math.radians(SKY_BASE_ANG - 0.05)) * dist) - z0 - 1.0) / bh)
    inst = bpy.data.objects.new(f"MID_house_{TAG}_{stats['placed']:03d}", None)
    inst.instance_type = "COLLECTION"; inst.instance_collection = src
    inst.empty_display_size = 2
    inst.location = Vector((cx, cy, z0))
    inst.rotation_euler = (0.0, 0.0, yaw)
    inst.scale = Vector((sx, sy, sz))
    inst["osm_id"] = str(b["osm_id"]); inst["building_tag"] = b["building_tag"]; inst["kind"] = kind
    inst["status"] = "OSM footprint ACCURATE-to-OSM; form UNVERIFIED"
    inst["UNVERIFIED"] = "house type/height/roof/colour proxy; far LOD if dist>=4750"
    inst["ground_slope_m"] = round(slope, 2); inst["dist_sky_cam_m"] = round(dist, 1)
    inst["low_lod"] = 1 if low_lod else 0
    col.objects.link(inst)
    stats["placed"] += 1; stats["kinds"][kind] = stats["kinds"].get(kind, 0) + 1
    c, s = math.cos(-b["yaw_long_axis_rad"]), math.sin(-b["yaw_long_axis_rad"])
    for o in crowns:
        if o.hide_render or "MEASURED" in str(o.get("status", "")):
            continue
        px, py = o.location.x - cx, o.location.y - cy
        if abs(px) > 400 or abs(py) > 400:
            continue
        lx, ly = px * c - py * s, px * s + py * c
        r = 0.6 * o.scale.x
        if abs(lx) < L / 2 + r and abs(ly) < S / 2 + r:
            o.hide_render = True; o.hide_viewport = True; o["hidden_by"] = TAG
            stats["crowns_hidden"] += 1
print("HOUSES", json.dumps(stats))
if SAVE:
    bpy.ops.wm.save_mainfile(); print("SAVED", bpy.data.filepath)
else:
    print("dry-run")
