"""Self-review fix: street cam was mostly empty dark ground + a large white slab.
Retarget onto a denser near-far house row (~3000,-2000 cluster), eye 1.7 m, look along houses.
RERUNNABLE. --save to write. Tag 20261015af.
"""
import bpy, json, math, os, sys
from mathutils import Vector
SAVE = "--save" in sys.argv
sc = bpy.context.scene
ROOT = bpy.path.abspath("//")
fp = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/af/house_footprints_far_20261015af.json")))["buildings"]
# prefer houses in the 3.5-4.75 km near-far half around the densest ESE cell
cents = []
for b in fp:
    if not b.get("centroid_local_m"): continue
    cx, cy = b["centroid_local_m"]
    d = b.get("z_dist_m") or math.hypot(cx, cy)
    if 3500 <= d < 4800 and 2800 <= cx <= 3400 and -2300 <= cy <= -1700:
        cents.append(Vector((cx, cy, 0)))
print("cluster n", len(cents))
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
# pick a point among houses with clear gap, looking at max houses in a cone
pts_xy = [(c.x, c.y) for c in cents]
best = None
for ix in range(2920, 3250, 6):
    for iy in range(-2150, -1800, 6):
        p = Vector((ix, iy, 0))
        near = [c for c in cents if 18 < (c - p).length < 100]
        if len(near) < 6: continue
        # keep >= 10 m from any footprint centroid
        if min((c - p).length for c in cents) < 10: continue
        for k in range(24):
            th = k * math.pi / 12
            d = Vector((math.cos(th), math.sin(th), 0))
            sec = [c for c in near if (c - p).normalized().dot(d) > 0.88]
            # prefer views that also have a house within 35 m dead ahead
            ahead = [c for c in sec if (c - p).length < 55]
            score = len(sec) * 2 + len(ahead) * 3
            if best is None or score > best[0]:
                best = (score, p.copy(), d.copy(), len(sec), len(ahead))
score, p, d, nsec, nahead = best
tgt = p + d * 70.0
print("STREET fix pick", tuple(p.xy), "dir", tuple(d.xy), "score", score, "sec", nsec, "ahead", nahead)
g0 = gz(p.x, p.y) or 30.0
gm = gz(tgt.x, tgt.y) or g0
# also nudge closeup toward same cluster if it was sparse
cx = sum(c.x for c in cents) / len(cents); cy = sum(c.y for c in cents) / len(cents)
gc = gz(cx, cy) or 30.0
def cam(name, loc, tgt, lens):
    o = bpy.data.objects.get(name)
    if not o:
        o = bpy.data.objects.new(name, bpy.data.cameras.new(name)); sc.collection.objects.link(o)
    o.location = Vector(loc)
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.data.lens = lens; o.data.clip_start = 0.1; o.data.clip_end = 60000
    o["TAG"] = "20261015af"
    print("CAM", name, tuple(round(v, 1) for v in loc), "->", tuple(round(v, 1) for v in tgt), lens)
cam("CAM_eye_houses_far_street_af", (p.x, p.y, g0 + 1.7), (tgt.x, tgt.y, gm + 4.5), 28)
cam("CAM_closeup_houses_far_af", (cx - 70.0, cy + 55.0, gc + 28.0), (cx + 10.0, cy - 10.0, gc + 3.0), 35)
# keep oblique aimed at same cluster
cam("CAM_oblique_houses_far_af", (cx - 750.0, cy + 550.0, gc + 380.0), (cx, cy, gc), 32)
if SAVE:
    bpy.ops.wm.save_mainfile(); print("SAVED")
