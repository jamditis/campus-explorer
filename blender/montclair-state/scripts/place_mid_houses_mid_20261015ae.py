"""2026-10-15 ~12:35 AM ET, tag 20261015ae. RERUNNABLE. --save to write.
Port of place_mid_houses_near_20261014ad.py to the houses_scatter_20261014z MID band 2.5-3.5 km ESE
(358 OSM ways not already in ad; geometry re-fetched by data/ccom_mid_distance/ae/fetch_geom_mid_20261015ae.py,
public OSM API 0.6, (c) OSM contributors, EPSG:6527 via pyproj, same origin).
Reuses protos MID_house_protos_20261014ad (rebuilt roofs, shared meshes, ad colour variation). No re-append.
Footprint position/orientation/size: ACCURATE-to-OSM. Form/height/roof/colour: UNVERIFIED. No lamps / no street furniture.
"""
import bpy, json, math, os, sys, random
from mathutils import Vector, Matrix

SAVE = "--save" in sys.argv
TAG = "20261015ae"
PTAG = "20261014ad"  # proto tag
ROOT = bpy.path.abspath("//")
JSON = os.path.join(ROOT, "data", "ccom_mid_distance", "ae", "house_footprints_mid_20261015ae.json")
ASSET = "/workspace/nj-scenes/assets/campus_assets_8.blend"
COL_NAME = f"MID_houses_mid_{TAG}"
PROTO_COL = f"MID_house_protos_{PTAG}"
TYPES = {  # name: (body_len_x, body_w_y, body_h)
    "House_Gable_Tan_1storey": (10.0, 8.0, 5.0),
    "House_Gable_Grey_2storey": (11.0, 9.0, 8.0),
    "House_Hip_Brick_2storey": (12.0, 10.0, 8.0),
    "House_Duplex_Tan": (14.0, 8.0, 7.0),
    "House_Flat_Apartments_Low": (18.0, 12.0, 11.0),
}
rng = random.Random(2026101500)
sc = bpy.context.scene
SKY_CAM = Vector((26.975, -13.051, 140.617))
EXCLUDE = [
    {"name": "CCOM", "xmin": -30, "xmax": 55, "ymin": -45, "ymax": 35},
    {"name": "Morehead", "xmin": -90, "xmax": -20, "ymin": -80, "ymax": 20},
    {"name": "LifeHall", "xmin": -120, "xmax": -40, "ymin": 40, "ymax": 160},
]
GROUND = ["Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho", "Context_ground_beyond_data", "Terrain_LiDAR_DTM_1m"]

# ---------------------------------------------------------------- protos (append once)
proto_parent = bpy.data.collections.get(PROTO_COL)
if proto_parent is None:
    raise SystemExit("protos missing: run ad first")
    proto_parent = bpy.data.collections.new(PROTO_COL)
    sc.collection.children.link(proto_parent)
    with bpy.data.libraries.load(ASSET, link=False) as (src, dst):
        dst.collections = [t for t in TYPES if t in src.collections]
    for c in dst.collections:
        c.name = c.name + "_" + TAG
        proto_parent.children.link(c)
    # rename appended materials so they never collide with the campus_assets link
    for c in proto_parent.children:
        for o in c.all_objects:
            o.name = o.name + "_" + TAG
            for i, m in enumerate(o.data.materials):
                if m and not m.name.endswith(TAG):
                    base = m.name.split(".")[0] + "_" + TAG
                    o.data.materials[i] = bpy.data.materials.get(base) or m
                    if o.data.materials[i] is m:
                        m.name = base
# exclude from view layer (instances still render)
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

# ---------------------------------------------------------------- per-instance colour variation
def vary(mat_name, palette, rough=0.85):
    m = bpy.data.materials.get(mat_name)
    if not m:
        print("MAT_MISSING", mat_name); return
    m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    for n in [n for n in nt.nodes if n.name.startswith("AD_")]:
        nt.nodes.remove(n)
    oi = nt.nodes.new("ShaderNodeObjectInfo"); oi.name = "AD_info"
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.name = "AD_ramp"
    cr.color_ramp.interpolation = "CONSTANT"
    els = cr.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position = 0.0; els[0].color = palette[0] + (1.0,)
    for i, col in enumerate(palette[1:], 1):
        e = els.new(i / len(palette)); e.color = col + (1.0,)
    nt.links.new(oi.outputs["Random"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.2
# modest, desaturated palettes (NJ suburban: asphalt shingle, vinyl siding, brick)
# colour variation already on the _20261014ad proto materials (no re-run)

# ---------------------------------------------------------------- ground ray
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

def pick(b):
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

# ---------------------------------------------------------------- build
col = bpy.data.collections.get(COL_NAME)
if col is None:
    col = bpy.data.collections.new(COL_NAME)
    sc.collection.children.link(col)
for o in list(col.objects):
    bpy.data.objects.remove(o, do_unlink=True)
col["TAG"] = TAG
col["UNVERIFIED"] = "OSM footprint position/orientation/size ACCURATE-to-OSM; house form/height/roof/colour UNVERIFIED proxies"

canopy = bpy.data.collections.get("MID_canopy_near_20261014ac")
crowns = [o for o in canopy.objects if o.type == "MESH"] if canopy else []
for o in crowns:  # restore crowns hidden by previous runs of this script
    if o.get("hidden_by") == TAG:
        o.hide_render = False; o.hide_viewport = False; del o["hidden_by"]

data = json.load(open(JSON))["buildings"]
stats = {"placed": 0, "skip": {}, "kinds": {}, "crowns_hidden": 0, "sightline_flag": 0}
SKY_BASE_ANG = math.degrees(math.atan2(0.0 - SKY_CAM.z, 21700.0))  # skyline base angle ~ -0.37 deg
for b in data:
    if not b.get("centroid_local_m"):
        stats["skip"]["no_geom"] = stats["skip"].get("no_geom", 0) + 1; continue
    cx, cy = b["centroid_local_m"]
    if in_exclude(cx, cy):
        stats["skip"]["campus"] = stats["skip"].get("campus", 0) + 1; continue
    tname, height, kind = pick(b)
    if tname is None:
        stats["skip"][kind] = stats["skip"].get(kind, 0) + 1; continue
    src = bpy.data.collections.get(tname + "_" + PTAG)
    bx, by, bh = TYPES[tname]
    L, S = b["mrr_long_m"], b["mrr_short_m"]
    sx = max(0.35, min(6.0, L / bx)); sy = max(0.35, min(6.0, S / by))
    if height:
        sz = height / bh
    else:
        sz = max(0.85, min(1.2, math.sqrt(sx * sy))) * rng.uniform(0.95, 1.05)
    # drape on footprint vertices
    zs = [ground_z(x, y) for x, y in b["footprint_local_m"][::max(1, len(b["footprint_local_m"]) // 8)]] + [ground_z(cx, cy)]
    zs = [z for z in zs if z is not None]
    if not zs:
        stats["skip"]["no_ground"] = stats["skip"].get("no_ground", 0) + 1; continue
    z0 = min(zs) - 0.35
    slope = max(zs) - min(zs)
    yaw = b["yaw_long_axis_rad"] + (math.pi if rng.random() < 0.5 else 0.0)
    # sightline check toward skyline (lab cam wedge -40..-25)
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
    inst["UNVERIFIED"] = "house type/height/roof/colour proxy; levels tag used where present"
    inst["ground_slope_m"] = round(slope, 2); inst["dist_sky_cam_m"] = round(dist, 1)
    col.objects.link(inst)
    stats["placed"] += 1; stats["kinds"][kind] = stats["kinds"].get(kind, 0) + 1
    # hide UNVERIFIED crowns sitting inside the footprint pad (rotated rect + 1.5 m)
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

# ---------------------------------------------------------------- cams
def cam(name, loc, tgt, lens):
    o = bpy.data.objects.get(name)
    if not o:
        o = bpy.data.objects.new(name, bpy.data.cameras.new(name)); sc.collection.objects.link(o)
    o.location = Vector(loc)
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.data.lens = lens; o.data.clip_start = 0.1; o.data.clip_end = 60000
    return o
CAMS = json.loads(os.environ.get("AE_CAMS", "{}"))
for k, v in CAMS.items():
    gz = ground_z(v[0][0], v[0][1]) if v[0][2] < 10 else 0.0
    loc = (v[0][0], v[0][1], (gz or 0.0) + v[0][2]) if v[0][2] < 10 else tuple(v[0])
    cam(k, loc, tuple(v[1]), v[2]); print("CAM", k, loc)
if SAVE:
    bpy.ops.wm.save_mainfile(); print("SAVED", bpy.data.filepath)
else:
    print("dry-run")
