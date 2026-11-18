"""tag 20261015ae self-review fix 2 (RERUNNABLE, --save): (a) street ribbons + up-facing roofs read too light/lavender
under the clear-sky dome vs the ortho -> asphalt 0.055 -> 0.028, roof palettes x0.65; (b) street eye cam moved onto an
OSM residential centreline in the densest ae cluster, looking along the street (was on a lawn facing a house row)."""
import bpy, json, math, os, sys
from mathutils import Vector
ROOT = bpy.path.abspath("//")
m = bpy.data.materials["MID_street_asphalt_20261015ae"]
next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.030, 0.029, 0.028, 1.0)
for mn in ("HouseProxy_Roof_Asphalt_20261014ad", "HouseProxy_Roof_Brown_20261014ad"):
    mt = bpy.data.materials[mn]; r = mt.node_tree.nodes["AD_ramp"].color_ramp
    if not mt.get("ae_dark2"):
        for e in r.elements: e.color = tuple(c * 0.65 for c in e.color[:3]) + (1.0,)
        mt["ae_dark2"] = 1
S = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/ae/streets_20261015ae.json")))["ways"]
H = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/ae/house_footprints_mid_20261015ae.json")))["buildings"]
cents = [Vector(b["centroid_local_m"]) for b in H]
best = None
for w in S:
    if w["highway"] != "residential": continue
    L = [Vector(p) for p in w["line_local_m"]]
    for a, b in zip(L, L[1:]):
        seg = b - a
        if seg.length < 90: continue
        d = seg.normalized(); p = a + d * 10.0
        n = sum(1 for c in cents if 0 < (c - p).dot(d) < 160 and abs((c - p).cross(d)) < 40)
        if best is None or n > best[0]: best = (n, p, d, w["osm_id"], w.get("name"))
n, p, d, wid, nm = best
gobs = [bpy.data.objects[k] for k in ("Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho")]
def gz(x, y):
    z0 = None
    for o in gobs:
        mi = o.matrix_world.inverted(); ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok:
            z = (o.matrix_world @ loc).z; z0 = z if z0 is None else max(z0, z)
    return z0
p = p + Vector((-d.y, d.x)) * 1.8  # right-hand lane-ish offset
t = p + d * 90.0
c = bpy.data.objects["CAM_eye_houses_mid_street_ae"]
c.location = Vector((p.x, p.y, gz(p.x, p.y) + 1.7)); tg = Vector((t.x, t.y, gz(t.x, t.y) + 2.5))
c.rotation_euler = (tg - c.location).to_track_quat("-Z", "Y").to_euler(); c.data.lens = 28
print("STREETCAM way", wid, nm, "houses_ahead", n, tuple(round(v, 1) for v in c.location))
if "--save" in sys.argv: bpy.ops.wm.save_mainfile(); print("SAVED")
