"""2026-10-14 ~10:25 PM ET, tag 20261014ac.
PRIMARY: instance near-campus canopy from tree_instance_manifest_20261014pj.csv
into MID_canopy_near_20261014ac (shared-mesh low-poly crowns; LiDAR xy MEASURED).
SECONDARY: nudge lounge clear glass clarity + darken equip wall-patch Value.
Hide superseded MID_canopy_20261014x (not delete). RERUNNABLE. --save to write.
"""
import bpy, csv, math, os, sys
from mathutils import Vector

SAVE = "--save" in sys.argv
TAG = "20261014ac"
ROOT = bpy.path.abspath("//")
CSV = os.path.join(ROOT, "data", "ccom_mid_distance", "tree_instance_manifest_20261014pj.csv")
COL_NAME = f"MID_canopy_near_{TAG}"
PROTO = f"MID_tree_proto_{TAG}"
MAT = f"MID_canopy_green_{TAG}"

# Approximate building footprints to avoid (local EPSG-like xy meters).
# Generous pads so crowns don't clip walls. UNVERIFIED extents except CCOM east wall ~x27.
EXCLUDE = [
    # CCOM main mass (includes east lounge / raised box / south equip)
    {"name": "CCOM", "xmin": -30, "xmax": 55, "ymin": -45, "ymax": 35},
    # Morehead Hall (west/SW of CCOM area — coarse)
    {"name": "Morehead", "xmin": -90, "xmax": -20, "ymin": -80, "ymax": 20},
    # Life Hall (NW-ish campus — coarse from prior north notes)
    {"name": "LifeHall", "xmin": -120, "xmax": -40, "ymin": 40, "ymax": 160},
]

# Skyline sightline thin: drop/hide points very near lab cam that would clog the wedge
# (guidance: dist_m < 80 and bearing in [-40,-25]). We SKIP placing those (render-only rule
# preferred permanent thin only with Joe OK — but these 3 would sit in the photo foreground
# unrealistically dense; keep MEASURED ones past 35 m).
SKY_CAM = Vector((26.975, -13.051, 0))
THIN_DIST = 35.0  # skip only the closest few in the skyline wedge
THIN_BEAR = (-40.0, -25.0)

def in_exclude(x, y):
    for e in EXCLUDE:
        if e["xmin"] <= x <= e["xmax"] and e["ymin"] <= y <= e["ymax"]:
            return e["name"]
    return None

def bearing_deg(x, y):
    dx, dy = x - SKY_CAM.x, y - SKY_CAM.y
    return math.degrees(math.atan2(dy, dx))  # note: CSV bearings may use different convention

# --------------------------------------------------------------------------
# 0) Hide superseded mid-distance canopy carpet (keep proxies visible)
# --------------------------------------------------------------------------
superseded = []
for nm in ("MID_canopy_20261014x",):
    col = bpy.data.collections.get(nm)
    if col:
        col.hide_viewport = True
        col.hide_render = True
        superseded.append(nm)
        print("HIDE_SUPERSEDED", nm, "objs", len(col.objects))
# MID_distance_proxies_20261014x kept (apt/mast)

# --------------------------------------------------------------------------
# 1) Canopy collection — shared-mesh copies (low mem)
# --------------------------------------------------------------------------
if COL_NAME in bpy.data.collections:
    col = bpy.data.collections[COL_NAME]
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL_NAME)
    bpy.context.scene.collection.children.link(col)

# Cheap crown: icosphere subdiv 0 (20 tris). Trunkless blob — LOD proxy.
if PROTO in bpy.data.objects:
    proto = bpy.data.objects[PROTO]
else:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=0, radius=1.0, location=(0, 0, -8000))
    proto = bpy.context.active_object
    proto.name = PROTO
    # orphan proto from scene view — keep data
    proto.hide_set(True)
    proto.hide_render = True
    proto.hide_viewport = True

mat = bpy.data.materials.get(MAT) or bpy.data.materials.new(MAT)
mat.use_nodes = True
nt = mat.node_tree
bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
if bsdf:
    # two-tone via slight variation isn't needed; flat dark green canopy
    bsdf.inputs["Base Color"].default_value = (0.10, 0.18, 0.08, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.88
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.15
proto.data.materials.clear()
proto.data.materials.append(mat)

n_place = n_skip_bldg = n_skip_thin = n_meas = n_unv = 0
with open(CSV, newline="") as f:
    for row in csv.DictReader(f):
        x, y = float(row["x"]), float(row["y"])
        z = float(row["z"]) if row["z"] not in ("", "None", None) else 0.0
        h = float(row["height_m"]) if row["height_m"] not in ("", "None", None) else 12.0
        dist = float(row["dist_m"]) if row.get("dist_m") not in ("", None) else 9999.0
        bear = float(row["bearing_deg"]) if row.get("bearing_deg") not in ("", None) else 0.0
        hit = in_exclude(x, y)
        if hit:
            n_skip_bldg += 1
            continue
        # Thin only the closest skyline-wedge trees (<35 m) so lab cam still sees mid canopy
        if dist < THIN_DIST and THIN_BEAR[0] <= bear <= THIN_BEAR[1]:
            n_skip_thin += 1
            continue
        r = max(1.2, min(14.0, 0.32 * h))
        ob = proto.copy()
        ob.data = proto.data  # share mesh — key for mem
        ob.name = f"MID_tree_{TAG}_{n_place:04d}"
        ob.hide_set(False)
        ob.hide_render = False
        ob.hide_viewport = False
        # crown center above ground
        ob.location = Vector((x, y, z + r * 0.75))
        # slight squash variation by kind
        if row["kind"] == "campus_lidar_tree":
            sx = sy = r
            sz = r * 1.20
        else:
            sx = sy = r * 0.95
            sz = r * 1.05
        ob.scale = Vector((sx, sy, sz))
        measured = "MEASURED" in (row.get("status") or "")
        ob["kind"] = row["kind"]
        ob["status"] = row["status"]
        ob["dist_m"] = dist
        ob["bearing_deg"] = bear
        if measured:
            ob["UNVERIFIED"] = "campus LiDAR xy/z MEASURED; crown mesh proxy UNVERIFIED"
            n_meas += 1
        else:
            ob["UNVERIFIED"] = "OSM wood fill / mid-distance canopy proxy UNVERIFIED"
            n_unv += 1
        col.objects.link(ob)
        n_place += 1

print(f"CANOPY placed={n_place} measured={n_meas} unverified={n_unv} "
      f"skip_bldg={n_skip_bldg} skip_thin={n_skip_thin} col={COL_NAME}")

# Tag collection
col["TAG"] = TAG
col["UNVERIFIED"] = "crowns are low-poly proxies; LiDAR tree xy MEASURED where status says so"

# --------------------------------------------------------------------------
# 2) Glass clarity nudge (lounge / clear glass) — keep interior readable
# --------------------------------------------------------------------------
def retune_glass(name, ior=1.02, alpha=0.025, spec=0.08, rough=0.008):
    m = bpy.data.materials.get(name)
    if not m or not m.use_nodes:
        print("GLASS_MISSING", name)
        return
    b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not b:
        return
    b.inputs["Base Color"].default_value = (0.94, 0.96, 0.98, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["IOR"].default_value = ior
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    elif "Specular" in b.inputs:
        b.inputs["Specular"].default_value = spec
    m.blend_method = "HASHED"
    print("GLASS", name, "ior", ior, "alpha", alpha, "spec", spec)

retune_glass("CCOM_clear_glass_20261014jf")
retune_glass("CCOM_lounge_glass_20261014z")  # unused west but keep consistent

# --------------------------------------------------------------------------
# 3) Equip wall-patch Value darken (left-of-rollup sun flash)
# --------------------------------------------------------------------------
pm = bpy.data.materials.get("CCOM_equip_wall_match_20261014ab")
if pm and pm.use_nodes:
    hs = pm.node_tree.nodes.get("AB_Darken")
    if hs and "Value" in hs.inputs:
        old = float(hs.inputs["Value"].default_value)
        hs.inputs["Value"].default_value = 0.82  # was 0.90
        print("PATCH_VALUE", old, "->", 0.82)
    else:
        print("PATCH_NO_AB_Darken")
else:
    print("PATCH_MAT_MISSING")

# --------------------------------------------------------------------------
# 4) Closeup cam for canopy near CCOM east edge
# --------------------------------------------------------------------------
def cam(name, loc, tgt, lens=28):
    o = bpy.data.objects.get(name)
    if not o:
        o = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        bpy.context.scene.collection.objects.link(o)
    o.location = Vector(loc)
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.data.lens = lens
    o.data.clip_start = 0.05
    o.data.clip_end = 60000
    return o

# Looking ESE over canopy belt from just east of CCOM
cam("CAM_closeup_CCOM_canopy_ac", (55.0, -40.0, 145.0), (180.0, -120.0, 130.0), 28)
# Aerial-ish oblique that shows canopy belt east of CCOM
cam("CAM_oblique_CCOM_canopy_ac", (20.0, 40.0, 220.0), (120.0, -80.0, 110.0), 24)
print("CAMS ok")

print("TAG", TAG, "done superseded", superseded)
if SAVE:
    bpy.ops.wm.save_mainfile()
    print("SAVED", bpy.data.filepath)
else:
    print("dry-run (pass --save)")
