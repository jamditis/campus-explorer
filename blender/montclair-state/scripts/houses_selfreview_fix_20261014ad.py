"""tag 20261014ad self-review fixes (RERUNNABLE, --save):
1) flat-roof parapet caps read pure white -> per-instance varied grey membrane material
2) darker/desaturated brick + trim (pastel pink under AgX)
3) Context_ground_beyond_data plane 39 m -> 0.5 m (was poking above BD_farfield in Passaic lowlands
   as a flat grey-green sheet; plane was set to skirt-min-5 before farfield existed)
4) street eye cam moved off a wall into an OSM-clear gap (>=15 m from footprints)
"""
import bpy, sys
from mathutils import Vector
TAG = "20261014ad"; SAVE = "--save" in sys.argv
def palette(mat, cols):
    m = bpy.data.materials[mat]; cr = m.node_tree.nodes["AD_ramp"].color_ramp
    for e, c in zip(cr.elements, cols): e.color = c + (1.0,)
# 1) membrane material for parapet caps
src = bpy.data.materials[f"HouseProxy_Roof_Asphalt_{TAG}"]
mm = bpy.data.materials.get(f"HouseProxy_FlatRoof_membrane_{TAG}") or src.copy()
mm.name = f"HouseProxy_FlatRoof_membrane_{TAG}"
cr = mm.node_tree.nodes["AD_ramp"].color_ramp
for e, c in zip(cr.elements, [(0.30,0.30,0.29),(0.38,0.38,0.37),(0.22,0.22,0.23),(0.44,0.43,0.41),(0.26,0.25,0.23),(0.34,0.33,0.31)]):
    e.color = c + (1.0,)
par = bpy.data.objects[f"HA_parapet_{TAG}"]
par.data.materials[0] = mm
# 2) brick + trim + siding tone
palette(f"HouseProxy_Brick_Red_{TAG}", [(0.28,0.12,0.085),(0.24,0.11,0.08),(0.32,0.16,0.11),(0.38,0.34,0.29),(0.21,0.10,0.075)])
palette(f"HouseProxy_Siding_Tan_{TAG}", [(0.50,0.44,0.33),(0.58,0.56,0.50),(0.42,0.40,0.35),(0.54,0.48,0.39),(0.44,0.46,0.47)])
palette(f"HouseProxy_Siding_Grey_{TAG}", [(0.36,0.37,0.39),(0.52,0.53,0.52),(0.32,0.36,0.38),(0.58,0.57,0.54),(0.40,0.38,0.35)])
t = bpy.data.materials[f"HouseProxy_Trim_White_{TAG}"]
b = next(n for n in t.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value = (0.66,0.66,0.63,1)
# 3) beyond plane
gp = bpy.data.objects["Context_ground_beyond_data"]
old = [round((gp.matrix_world @ v.co).z, 2) for v in gp.data.vertices]
for v in gp.data.vertices:
    v.co.z = (gp.matrix_world.inverted() @ Vector((0, 0, 0.5))).z
gp["z_was_20261014ad"] = old[0]
print("BEYOND z", old, "->", [round((gp.matrix_world @ v.co).z, 2) for v in gp.data.vertices])
# 4) cam
sc = bpy.context.scene
def gz(x, y):
    best = None
    for n in ("Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho"):
        o = bpy.data.objects[n]; mi = o.matrix_world.inverted()
        ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok:
            z = (o.matrix_world @ loc).z; best = z if best is None else max(best, z)
    return best
c = bpy.data.objects["CAM_eye_houses_street_ad"]
c.location = Vector((2404.0, -842.0, gz(2404, -842) + 1.7))
c.rotation_euler = (Vector((1300.0, -480.0, 112.0)) - c.location).to_track_quat("-Z", "Y").to_euler()
c.data.lens = 30
print("CAM", tuple(round(v, 2) for v in c.location))
# collection sizes (for HIDE planning)
print("COLS", sorted([(len(cc.all_objects), cc.name) for cc in bpy.data.collections if cc.users and len(cc.all_objects) > 150], reverse=True)[:14])
if SAVE:
    bpy.ops.wm.save_mainfile(); print("SAVED")
