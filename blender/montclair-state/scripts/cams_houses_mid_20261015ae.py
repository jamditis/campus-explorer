"""2026-10-15 tag 20261015ae. Cams for the 2.5-3.5 km OSM house band. --save to write.
Street cam: auto-picked open spot (>=11 m from every OSM footprint vertex/centroid) in the densest cluster,
looking at the mean of houses 25-110 m away. No lamps/furniture."""
import bpy, json, math, os, sys
from mathutils import Vector
SAVE = "--save" in sys.argv
sc = bpy.context.scene
ROOT = bpy.path.abspath("//")
fp = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/ae/house_footprints_mid_20261015ae.json")))["buildings"]
def gz(x, y):
    best = None
    for n in ("Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho"):
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
    o["TAG"] = "20261015ae"
    print("CAM", name, tuple(round(v, 1) for v in loc), "->", tuple(round(v, 1) for v in tgt), lens)
    return o
pts = [tuple(p) for b in fp for p in b["footprint_local_m"]] + [tuple(b["centroid_local_m"]) for b in fp]
cents = [Vector(b["centroid_local_m"]) for b in fp]
best = None
for ix in range(2450, 3050, 6):
    for iy in range(-2100, -1600, 6):
        p = Vector((ix, iy))
        if min((p - Vector(q)).length for q in pts if abs(q[0]-ix) < 30 and abs(q[1]-iy) < 30) if any(abs(q[0]-ix) < 30 and abs(q[1]-iy) < 30 for q in pts) else 99 < 11:
            continue
        near = [c for c in cents if 25 < (c - p).length < 110]
        if len(near) < 6: continue
        for k in range(16):
            th = k * math.pi / 8; d = Vector((math.cos(th), math.sin(th)))
            sec = [c for c in near if (c - p).normalized().dot(d) > 0.92]
            if best is None or len(sec) > best[0]:
                best = (len(sec), p.copy(), p + d * 70.0)
score, p, m = best
print("STREET pick", tuple(p), "score", score)
g0 = gz(p.x, p.y); gm = gz(m.x, m.y)
cam("CAM_eye_houses_mid_street_ae", (p.x, p.y, g0 + 1.7), (m.x, m.y, gm + 3.0), 30)
cx, cy = 2780.0, -1850.0; gc = gz(cx, cy) or 30.0
cam("CAM_oblique_houses_mid_ae", (2050.0, -1050.0, gc + 420.0), (cx, cy, gc), 32)
cam("CAM_closeup_houses_mid_ae", (cx - 80.0, cy + 70.0, gc + 42.0), (cx + 15.0, cy - 15.0, gc + 2.0), 35)
if SAVE:
    bpy.ops.wm.save_mainfile(); print("SAVED")
