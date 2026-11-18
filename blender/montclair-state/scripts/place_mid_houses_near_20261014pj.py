"""Instance low-poly houses from neighborhoods_midnear_20261014pj.json.
Run under main .lock (NOT parallel while main locked):
  blender_slot.sh -b montclair_state.blend --python scripts/place_mid_houses_near_20261014pj.py -- --save
Assets: assets/campus_assets_8.blend collections House_*
All IDs UNVERIFIED.
"""
import bpy, json, os, sys, math, random
from mathutils import Vector

ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAVE = "--save" in ARGV
LIMIT = None
if "--limit" in ARGV:
    LIMIT = int(ARGV[ARGV.index("--limit") + 1])
ROOT = bpy.path.abspath("//")
JSON = os.path.join(ROOT, "data", "ccom_mid_distance", "neighborhoods_midnear_20261014pj.json")
ASSET = "/workspace/nj-scenes/assets/campus_assets_8.blend"
TAG = "20261014pj"
COL_NAME = f"MID_houses_near_{TAG}"
TYPES = [
    "House_Gable_Tan_1storey",
    "House_Gable_Grey_2storey",
    "House_Hip_Brick_2storey",
    "House_Duplex_Tan",
    "House_Flat_Apartments_Low",
]
rng = random.Random(20261014)

# load asset collections (link)
with bpy.data.libraries.load(ASSET, link=True) as (src, dst):
    dst.collections = [t for t in TYPES if t in src.collections]

if COL_NAME in bpy.data.collections:
    col = bpy.data.collections[COL_NAME]
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL_NAME)
    bpy.context.scene.collection.children.link(col)

data = json.load(open(JSON))
buildings = data["buildings"]
if LIMIT:
    buildings = buildings[:LIMIT]

def pick_type(b):
    tag = (b.get("building_tag") or "yes").lower()
    h = (b.get("size_m_estimate") or {}).get("h") or 9
    if tag in ("apartments", "yes") and h >= 12:
        return "House_Flat_Apartments_Low"
    if tag in ("terrace", "semidetached_house"):
        return "House_Duplex_Tan"
    if h >= 10:
        return rng.choice(["House_Gable_Grey_2storey", "House_Hip_Brick_2storey"])
    return rng.choice(["House_Gable_Tan_1storey", "House_Gable_Grey_2storey", "House_Duplex_Tan"])

n = 0
for b in buildings:
    tname = pick_type(b)
    if tname not in bpy.data.collections:
        continue
    src_col = bpy.data.collections[tname]
    inst = bpy.data.objects.new(f"MID_house_{TAG}_{n:04d}", None)
    inst.instance_type = "COLLECTION"
    inst.instance_collection = src_col
    xy = b["centroid_xy_m"]
    # ground z: leave 0; main stream should raycast/drape — mark prop
    inst.location = Vector((xy[0], xy[1], 0.0))
    # scale to footprint width roughly (asset ~10–12 m wide)
    w = (b.get("size_m_estimate") or {}).get("w") or 10
    s = max(0.5, min(2.5, w / 10.0))
    inst.scale = Vector((s, s, s))
    inst.rotation_euler[2] = rng.random() * math.tau  # UNVERIFIED yaw
    inst["osm_id"] = b.get("osm_id")
    inst["status"] = "UNVERIFIED"
    inst["UNVERIFIED"] = "mid-distance house proxy; yaw/scale approximate; drape z"
    inst["needs_ground_drape"] = True
    col.objects.link(inst)
    n += 1
print(f"instanced {n} houses in {COL_NAME} from {JSON}")
if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("SAVED")
else:
    print("dry-run (pass --save to write)")
