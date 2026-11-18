"""tag 20261016bs (2): Cole Hall polish. Idempotent; SAVE=1 to write.
1. COLE_win_glass_bq: was flat black (rough 0.35) -> slightly reflective (rough 0.08, spec 0.7) with faint interior
   depth (object-space noise between near-black and a dim warm interior tone; interior look UNVERIFIED).
2. 2020 north addition gable: white rake trim along both gable edges (drone photo 2020 shows a light band on the
   rakes; width/depth UNVERIFIED), placed from the addition mesh's own north-gable apex + eave corners.
"""
import bpy, bmesh, os, math
from mathutils import Vector
m = bpy.data.materials["COLE_win_glass_bq"]; nt = m.node_tree; bs = nt.nodes["Principled BSDF"]
for n in [n for n in nt.nodes if n.name.startswith("bs_")]: nt.nodes.remove(n)
bs.inputs["Roughness"].default_value = 0.08; bs.inputs["Specular IOR Level"].default_value = 0.7
tc = nt.nodes.new("ShaderNodeTexCoord"); tc.name = "bs_tc"
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.name = "bs_nz"; nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 2
mr = nt.nodes.new("ShaderNodeMapRange"); mr.name = "bs_mr"; mr.inputs["From Min"].default_value = 0.45; mr.inputs["From Max"].default_value = 0.72
mx = nt.nodes.new("ShaderNodeMix"); mx.name = "bs_mx"; mx.data_type = "RGBA"
mx.inputs["A"].default_value = (0.014, 0.018, 0.024, 1); mx.inputs["B"].default_value = (0.055, 0.05, 0.045, 1)
nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
nt.links.new(mr.outputs["Result"], mx.inputs["Factor"]); nt.links.new(mx.outputs["Result"], bs.inputs["Base Color"])
m["bs_glass"] = "rough 0.08 spec 0.7 + interior noise (UNVERIFIED)"; print("GLASS updated")

ad = [o for o in bpy.data.objects if o.name.startswith("Cole Hall 2020 north addition")][0]
mw = ad.matrix_world; V = [mw @ v.co for v in ad.data.vertices]
a = Vector((-116.6, -60.8, 0)); b = Vector((-94.1, -66.0, 0)); d = (b - a); d.z = 0; L = d.length; d.normalize()
nrm = Vector((-d.y, d.x, 0))
if nrm.dot(Vector((-105.35, -63.4, 0)) - Vector((-107.0, -80.0, 0))) < 0: nrm = -nrm   # outward = north
near = [v for v in V if abs((v - a).dot(nrm)) < 0.8 and -1 < (v - a).dot(d) < L + 1]
apex = max(near, key=lambda v: v.z)
ev = [v for v in near if 142.3 < v.z < 144.5] or near
c1 = min(ev, key=lambda v: (v - a).dot(d)); c2 = max(ev, key=lambda v: (v - a).dot(d))
print("ADD_GABLE apex", tuple(round(x, 2) for x in apex), "c1", tuple(round(x, 2) for x in c1), "c2", tuple(round(x, 2) for x in c2), "nnear", len(near))
nm = "COLE_add_rake_trim_bs"
o = bpy.data.objects.get(nm)
if o: bpy.data.meshes.remove(o.data)
bm = bmesh.new()
W, D, OUT = 0.42, 0.28, 0.06
plane_pt = max(near, key=lambda v: (v - a).dot(nrm))   # outermost face plane of the gable end
off = (plane_pt - a).dot(nrm) + OUT
for p0, p1 in ((c1, apex), (c2, apex)):
    p0 = p0.copy(); p1 = p1.copy()
    p0 += nrm * (off - (p0 - a).dot(nrm)); p1 += nrm * (off - (p1 - a).dot(nrm))
    t = (p1 - p0).normalized(); up = nrm.cross(t).normalized()
    if up.z < 0: up = -up
    p0e = p0 - t * 0.35; p1e = p1 + t * 0.15
    cs = []
    for P in (p0e, p1e):
        for (u, w) in ((0, 0), (1, 0), (1, 1), (0, 1)):
            cs.append(bm.verts.new(P + up * (W * (u - 0.35)) - nrm * (D * w)))
    q = cs
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([q[i] for i in f])
me = bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials["COLE_win_trim_white_br"])
o = bpy.data.objects.new(nm, me); ad.users_collection[0].objects.link(o)
o["bs_note"] = "rake trim on addition gable; position from addition mesh; size UNVERIFIED"
print("RAKE built", nm)
if os.environ.get("SAVE") == "1": bpy.ops.wm.save_mainfile(); print("SAVED")
