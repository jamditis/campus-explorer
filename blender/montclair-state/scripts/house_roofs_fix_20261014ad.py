"""tag 20261014ad self-review fix (RERUNNABLE, --save): the House_* protos from campus_assets_8.blend have
mis-pivoted roof slabs (roof_N/roof_S sit BESIDE the body like wings, below the eave; body top shows flat).
Rebuild proper gable / hip roof meshes on the appended _20261014ad proto copies only (asset file untouched).
"""
import bpy, bmesh, sys
from mathutils import Vector
TAG = "20261014ad"; SAVE = "--save" in sys.argv
OV = 0.35  # eave overhang
SPEC = {  # proto prefix: (body obj, half L, half W, eave z, rise, kind, roof objs to hide)
    "HG1": ("HG1_body", 5.0, 4.0, 5.0, 2.3, "gable", ["HG1_roof_N", "HG1_roof_S"]),
    "HG2": ("HG2_body", 5.5, 4.5, 8.0, 2.8, "gable", ["HG2_roof_N", "HG2_roof_S"]),
    "HD":  ("HD_body", 7.0, 4.0, 7.0, 2.4, "gable", ["HD_roof_N", "HD_roof_S"]),
    "HH":  ("HH_body", 6.0, 5.0, 8.0, 2.6, "hip", ["HH_roof_N", "HH_roof_S", "HH_hip_cap"]),
}
for k, (body, hl, hw, ez, rise, kind, olds) in SPEC.items():
    bo = bpy.data.objects[f"{body}_{TAG}"]
    old0 = bpy.data.objects[f"{olds[0]}_{TAG}"]
    roofmat = old0.data.materials[0]; wallmat = bo.data.materials[0]
    col = old0.users_collection[0]
    name = f"{k}_roof_fixed_{TAG}"
    ob = bpy.data.objects.get(name)
    me = bpy.data.meshes.new(name + "_me")
    L, W = hl + OV, hw + OV
    e = ez - 0.12  # eave edge slightly below wall top so no gap
    bm = bmesh.new()
    if kind == "gable":
        v = [bm.verts.new(p) for p in [(-L, -W, e), (L, -W, e), (L, W, e), (-L, W, e), (-L, 0, ez + rise), (L, 0, ez + rise)]]
        fs = [bm.faces.new((v[0], v[1], v[5], v[4])), bm.faces.new((v[2], v[3], v[4], v[5]))]
        g = [bm.faces.new((v[1], v[2], v[5])), bm.faces.new((v[3], v[0], v[4]))]
        for f in fs: f.material_index = 0
        for f in g: f.material_index = 1
        # closing underside so the roof is a closed solid
        u = bm.faces.new((v[3], v[2], v[1], v[0])); u.material_index = 0
    else:
        r = max(0.5, hl - hw)
        v = [bm.verts.new(p) for p in [(-L, -W, e), (L, -W, e), (L, W, e), (-L, W, e), (-r, 0, ez + rise), (r, 0, ez + rise)]]
        for f in [(v[0], v[1], v[5], v[4]), (v[2], v[3], v[4], v[5]), (v[1], v[2], v[5]), (v[3], v[0], v[4]), (v[3], v[2], v[1], v[0])]:
            bm.faces.new(f).material_index = 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.materials.append(roofmat); me.materials.append(wallmat)
    if ob is None:
        ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    else:
        old_me = ob.data; ob.data = me; bpy.data.meshes.remove(old_me)
    for n in olds:
        o = bpy.data.objects.get(f"{n}_{TAG}")
        if o and o.name in col.objects:
            col.objects.unlink(o)  # kept as orphan-safe data? store in hidden holder
            holder = bpy.data.collections.get(f"MID_house_roofs_broken_{TAG}") or bpy.data.collections.new(f"MID_house_roofs_broken_{TAG}")
            if o.name not in holder.objects: holder.objects.link(o)
            holder.use_fake_user = True
    print("ROOF", k, kind, "eave", ez, "ridge", ez + rise)
# chimney on HG1 must clear the new roof: ridge 7.3 at y=0, chimney at y 0.25-0.75 -> roof there ~7.0
ch = bpy.data.objects.get(f"HG1_chimney_{TAG}")
if ch:
    ch["z_shift_ad"] = 1.0
    ch.location.z = ch.get("z_base_ad", ch.location.z) + 1.0 if "z_base_ad" in ch else ch.location.z + 1.0
    ch["z_base_ad"] = ch.location.z - 1.0
    print("CHIMNEY z", ch.location.z)
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")
