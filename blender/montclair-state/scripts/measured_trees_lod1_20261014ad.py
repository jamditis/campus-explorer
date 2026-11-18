"""tag 20261014ad SECONDARY (RERUNNABLE, --save): MEASURED campus LiDAR crowns in MID_canopy_near_20261014ac
-> campus_trees_v2 LOD1 copies (shared linked mesh data, copied from existing Trees_assets_LiDAR T_* templates).
If a T_* tree already stands within DUP_R m of the MEASURED point, the ico is just hidden (duplicate).
Ico crowns are hidden (hidden_by=20261014ad_lod1), never deleted. Trees go in MID_trees_measured_lod1_20261014ad.
"""
import bpy, sys, math, random
from mathutils import Vector, kdtree
SAVE = "--save" in sys.argv; TAG = "20261014ad"; DUP_R = 4.0
rng = random.Random(1015)
can = bpy.data.collections["MID_canopy_near_20261014ac"]
T = [o for o in bpy.data.collections["Trees_assets_LiDAR"].all_objects if o.name.startswith("T_")]
print("T count", len(T), "types", {o.type for o in T})
ex = T[0]; print("T example", ex.name, ex.type, ex.data.name if ex.data else None, ex.instance_type, ex.instance_collection.name if ex.instance_collection else None,
      tuple(round(v,2) for v in ex.location), tuple(round(v,2) for v in ex.scale), ex.dimensions[:], ex.data.library.filepath if ex.data and ex.data.library else None)
datas = {}
for o in T:
    k = o.data.name if o.data else (o.instance_collection.name if o.instance_collection else None)
    datas.setdefault(k, []).append(o)
print("T variants", {k: len(v) for k, v in datas.items()})
kd = kdtree.KDTree(len(T))
for i, o in enumerate(T): kd.insert(o.location, i)
kd.balance()
# templates: per variant, height of a unit-scale instance
tmpl = []
for k, v in datas.items():
    if "limbed" in str(k): continue
    o = v[0]; h = o.dimensions.z / max(o.scale.z, 1e-6)
    tmpl.append((k, o, h))
print("TEMPLATES", [(k, round(h, 1)) for k, o, h in tmpl])
col = bpy.data.collections.get(f"MID_trees_measured_lod1_{TAG}")
if col is None:
    col = bpy.data.collections.new(f"MID_trees_measured_lod1_{TAG}"); bpy.context.scene.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
n_dup = n_new = 0
for o in can.objects:
    if "MEASURED" not in str(o.get("status", "")): continue
    if o.get("hidden_by") == TAG + "_lod1":
        o.hide_render = False; o.hide_viewport = False
    r = o.scale.x; zc = o.location.z; ground = zc - r * 0.75
    h = max(4.0, r / 0.32)  # inverse of ac crown radius rule (r = 0.32 h)
    p = Vector((o.location.x, o.location.y, 0)); co, idx, d = kd.find(Vector((p.x, p.y, T[0].location.z)))
    dxy = math.hypot(co.x - p.x, co.y - p.y)
    o.hide_render = True; o.hide_viewport = True; o["hidden_by"] = TAG + "_lod1"
    if dxy < DUP_R:
        n_dup += 1; continue
    k, src, th = min(tmpl, key=lambda t: abs(t[2] - h) + rng.random() * 2.0)
    nob = src.copy(); col.objects.link(nob)
    s = h / th
    nob.location = Vector((p.x, p.y, ground - 0.2)); nob.scale = Vector((s, s, s))
    nob.rotation_euler = (0, 0, rng.random() * math.tau)
    nob.name = f"MID_lod1_{TAG}_{n_new:03d}"; nob["status"] = "LiDAR xy/z/height MEASURED; species/mesh UNVERIFIED"
    n_new += 1
print("LOD1 swap new", n_new, "dup_hidden", n_dup)
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")
