"""tag 20261015ag cams (RERUNNABLE, --save).
- CAM_oblique_streets_trees_ag: oblique over mid streets+trees
- CAM_eye_streets_trees_brookwood_ag: eye on Brookwood (or ae street with trees)
- CAM_closeup_street_trees_ag: close-up of street trees
Keep CAM_eye_CCOM_lab_skyline unchanged.
"""
import bpy, json, math, os, sys
from mathutils import Vector
SAVE = "--save" in sys.argv
TAG = "20261015ag"
sc = bpy.context.scene
ROOT = bpy.path.abspath("//")

gobs = [bpy.data.objects[n] for n in (
    "Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho", "Context_ground_beyond_data"
) if n in bpy.data.objects]

def gz(x, y):
    best = None
    for o in gobs:
        mi = o.matrix_world.inverted()
        ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok:
            z = (o.matrix_world @ loc).z
            best = z if best is None else max(best, z)
    return best

# tree locations from collection
col = bpy.data.collections.get(f"MID_street_trees_{TAG}")
trees = []
if col:
    for o in col.objects:
        trees.append(Vector((o.location.x, o.location.y, o.location.z)))
print("trees in col", len(trees), flush=True)

# Brookwood from ae streets if named
streets = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/ae/streets_20261015ae.json")))
brook = None
for w in streets["ways"]:
    if (w.get("name") or "").lower().find("brookwood") >= 0:
        brook = w
        break
# pick street eye: prefer near OSM trees or densify cluster
def cam(name, loc, tgt, lens):
    o = bpy.data.objects.get(name)
    if not o:
        o = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        sc.collection.objects.link(o)
    o.location = Vector(loc)
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.data.lens = lens
    o.data.clip_start = 0.1
    o.data.clip_end = 60000
    o["TAG"] = TAG
    print("CAM", name, tuple(round(v, 1) for v in loc), "->", tuple(round(v, 1) for v in tgt), lens, flush=True)

# cluster of trees around Brookwood / mid band
if brook:
    line = brook["line_local_m"]
    mid = line[len(line) // 2]
    # find a point on Brookwood with trees nearby
    best = None
    for i, p in enumerate(line[::max(1, len(line)//20)]):
        px, py = p[0], p[1]
        near = [t for t in trees if math.hypot(t.x - px, t.y - py) < 80]
        if best is None or len(near) > best[0]:
            best = (len(near), px, py, near)
    if best and best[0] > 0:
        bx, by = best[1], best[2]
    else:
        bx, by = mid[0], mid[1]
    print("Brookwood cam anchor", bx, by, "near_trees", best[0] if best else 0, flush=True)
else:
    # fallback: densest tree cell in ae bbox
    bx = by = None
    bestn = 0
    for cx in range(1200, 3200, 40):
        for cy in range(-2600, -400, 40):
            n = sum(1 for t in trees if abs(t.x - cx) < 60 and abs(t.y - cy) < 60)
            if n > bestn:
                bestn = n; bx, by = cx, cy
    print("fallback densest", bx, by, bestn, flush=True)

g0 = gz(bx, by) or 40.0
# look along approximate ESE street direction
look = Vector((bx + 90.0, by - 35.0, g0 + 5.0))
# if trees ahead, aim at their mean
ahead = [t for t in trees if 15 < math.hypot(t.x - bx, t.y - by) < 120]
if ahead:
    mx = sum(t.x for t in ahead) / len(ahead)
    my = sum(t.y for t in ahead) / len(ahead)
    look = Vector((mx, my, g0 + 6.0))

cam("CAM_eye_streets_trees_brookwood_ag", (bx, by, g0 + 1.7), tuple(look), 28)

# closeup: nearest cluster of 3+ trees
bestc = None
for t in trees:
    near = [u for u in trees if math.hypot(u.x - t.x, u.y - t.y) < 35]
    if bestc is None or len(near) > bestc[0]:
        bestc = (len(near), t, near)
tc = bestc[1]
cx = sum(u.x for u in bestc[2]) / len(bestc[2])
cy = sum(u.y for u in bestc[2]) / len(bestc[2])
gc = gz(cx, cy) or g0
cam("CAM_closeup_street_trees_ag",
    (cx - 28.0, cy + 22.0, gc + 14.0),
    (cx + 5.0, cy - 3.0, gc + 4.0), 35)

# oblique over mid streets+trees (ae band centre ~2000,-1500)
ox, oy = 2100.0, -1600.0
if trees:
    ox = sum(t.x for t in trees) / len(trees)
    oy = sum(t.y for t in trees) / len(trees)
go = gz(ox, oy) or 40.0
cam("CAM_oblique_streets_trees_ag",
    (ox - 650.0, oy + 480.0, go + 320.0),
    (ox, oy, go), 32)

# confirm lab cam exists
lab = bpy.data.objects.get("CAM_eye_CCOM_lab_skyline")
print("lab cam present", bool(lab), flush=True)

if SAVE:
    bpy.ops.wm.save_mainfile()
    print("SAVED", flush=True)
