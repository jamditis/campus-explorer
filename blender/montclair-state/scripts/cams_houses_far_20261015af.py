"""2026-10-15 tag 20261015af. Cams for the 3.5-6 km OSM house band. --save to write.
No OSM streets in this band (ae streets stop ~3.5 km). Street cam: clear ground in densest
near-far cluster looking at houses. No lamps/furniture.
"""
import bpy, json, math, os, sys
from mathutils import Vector
SAVE = "--save" in sys.argv
sc = bpy.context.scene
ROOT = bpy.path.abspath("//")
fp = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/af/house_footprints_far_20261015af.json")))["buildings"]
def gz(x, y):
    best = None
    for n in ("Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho", "Context_ground_beyond_data"):
        o = bpy.data.objects.get(n)
        if not o: continue
        mi = o.matrix_world.inverted()
        ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok:
            z = (o.matrix_world @ loc).z; best = z if best is None else max(best, z)
    return best
def cam(name, loc, tgt, lens):
    o = bpy.data.objects.get(name)
    if not o:
        o = bpy.data.objects.new(name, bpy.data.cameras.new(name)); sc.collection.objects.link(o)
    o.location = Vector(loc); o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.data.lens = lens; o.data.clip_start = 0.1; o.data.clip_end = 60000
    o["TAG"] = "20261015af"
    print("CAM", name, tuple(round(v, 1) for v in loc), "->", tuple(round(v, 1) for v in tgt), lens)
    return o
pts = [tuple(p) for b in fp for p in b["footprint_local_m"]] + [tuple(b["centroid_local_m"]) for b in fp]
cents = [Vector(b["centroid_local_m"]) for b in fp]
# Prefer denser cluster nearer the ESE wedge (~3000,-2000) over far south (-4200)
best = None
for ix in range(2850, 3450, 8):
    for iy in range(-2300, -1700, 8):
        p = Vector((ix, iy))
        near_pts = [q for q in pts if abs(q[0]-ix) < 40 and abs(q[1]-iy) < 40]
        if near_pts:
            md = min((p - Vector(q)).length for q in near_pts)
            if md < 12:
                continue
        else:
            # need some houses nearby overall
            if min((p - c).length for c in cents) > 90:
                continue
        near = [c for c in cents if 30 < (c - p).length < 140]
        if len(near) < 5: continue
        for k in range(16):
            th = k * math.pi / 8; d = Vector((math.cos(th), math.sin(th)))
            sec = [c for c in near if (c - p).normalized().dot(d) > 0.9]
            if best is None or len(sec) > best[0]:
                best = (len(sec), p.copy(), p + d * 90.0)
if best is None:
    # fallback: clear ground near median
    cx0, cy0 = 3100.0, -1950.0
    best = (0, Vector((cx0, cy0)), Vector((cx0 + 80, cy0 - 40)))
    print("STREET fallback", flush=True)
score, p, m = best
print("STREET pick", tuple(p), "score", score, flush=True)
g0 = gz(p.x, p.y) or 25.0; gm = gz(m.x, m.y) or g0
cam("CAM_eye_houses_far_street_af", (p.x, p.y, g0 + 1.7), (m.x, m.y, gm + 3.0), 28)
# dense cluster center for oblique/closeup — use median of near-far half (dist<4750) if available
near_far = [b for b in fp if (b.get("z_dist_m") or 9999) < 4750]
use = near_far if len(near_far) >= 40 else fp
cx = sum(b["centroid_local_m"][0] for b in use) / len(use)
cy = sum(b["centroid_local_m"][1] for b in use) / len(use)
gc = gz(cx, cy) or 30.0
cam("CAM_oblique_houses_far_af", (cx - 900.0, cy + 700.0, gc + 520.0), (cx, cy, gc), 32)
cam("CAM_closeup_houses_far_af", (cx - 100.0, cy + 90.0, gc + 48.0), (cx + 20.0, cy - 20.0, gc + 2.0), 35)
# ensure lab skyline cam still present
if "CAM_eye_CCOM_lab_skyline" not in bpy.data.objects:
    print("WARN missing CAM_eye_CCOM_lab_skyline")
else:
    print("KEEP CAM_eye_CCOM_lab_skyline")
if SAVE:
    bpy.ops.wm.save_mainfile(); print("SAVED")
