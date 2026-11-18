"""Place MID near-campus canopy from parallel 20261014pj manifest.
Run under main .lock when ready (NOT from parallel while main is locked):
  ../../tools/blender_slot.sh -b montclair_state.blend --python scripts/place_mid_canopy_near_20261014pj.py -- --save
Low-poly icosphere proxies; swap for campus_trees_v2 assets later.
campus_lidar_tree xy = MEASURED; wood fills = UNVERIFIED.
"""
import bpy, csv, os, sys
from mathutils import Vector

ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAVE = "--save" in ARGV
ROOT = bpy.path.abspath("//")
CSV = os.path.join(ROOT, "data", "ccom_mid_distance", "tree_instance_manifest_20261014pj.csv")
TAG = "20261014pj"
COL_NAME = f"MID_canopy_near_{TAG}"

if COL_NAME in bpy.data.collections:
    col = bpy.data.collections[COL_NAME]
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL_NAME)
    bpy.context.scene.collection.children.link(col)

proto_name = f"MID_tree_proto_{TAG}"
if proto_name not in bpy.data.objects:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, location=(0, 0, -5000))
    proto = bpy.context.active_object
    proto.name = proto_name
    proto.hide_set(True)
    proto.hide_render = True
else:
    proto = bpy.data.objects[proto_name]

mat_name = f"MID_canopy_green_{TAG}"
mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.12, 0.22, 0.10, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.85
if proto.data.materials:
    proto.data.materials[0] = mat
else:
    proto.data.materials.append(mat)

n = 0
with open(CSV, newline="") as f:
    for row in csv.DictReader(f):
        x, y = float(row["x"]), float(row["y"])
        z = float(row["z"]) if row["z"] not in ("", "None", None) else 0.0
        h = float(row["height_m"]) if row["height_m"] not in ("", "None", None) else 12.0
        r = max(1.5, 0.35 * h)
        ob = proto.copy()
        ob.data = proto.data  # share mesh
        ob.name = f"MID_tree_{TAG}_{n:04d}"
        ob.hide_set(False)
        ob.hide_render = False
        ob.location = Vector((x, y, z + r * 0.85))
        ob.scale = Vector((r, r, r * 1.15))
        ob["kind"] = row["kind"]
        ob["status"] = row["status"]
        ob["UNVERIFIED"] = (
            "campus LiDAR xy MEASURED; mesh proxy"
            if "MEASURED" in row["status"]
            else "mid-distance canopy proxy UNVERIFIED"
        )
        col.objects.link(ob)
        n += 1
print(f"placed {n} canopy proxies in {COL_NAME}")
if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("SAVED")
else:
    print("dry-run (pass --save to write)")
