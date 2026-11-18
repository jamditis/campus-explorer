import bpy
from mathutils import Vector
def gz(x, y):
    best=None
    for n in ("Context_skirt_3DEP_ortho_4km","BD_farfield_3DEP_ortho"):
        o=bpy.data.objects[n]; mi=o.matrix_world.inverted()
        ok,loc,*_=o.ray_cast(mi@Vector((x,y,3000)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            z=(o.matrix_world@loc).z; best=z if best is None else max(best,z)
    return best
c=bpy.data.objects["CAM_eye_houses_street_ad"]
c.location=Vector((2060.0,-780.0,gz(2060,-780)+1.7))
t=Vector((2200.0,-830.0,gz(2200,-830)+3.0))
c.rotation_euler=(t-c.location).to_track_quat("-Z","Y").to_euler(); c.data.lens=32
print("CAM",tuple(round(v,2) for v in c.location),"tgt",tuple(round(v,2) for v in t))
import sys
TAG="20261014ad"
cr=bpy.data.materials[f"HouseProxy_Brick_Red_{TAG}"].node_tree.nodes["AD_ramp"].color_ramp
for e,cc in zip(cr.elements,[(0.17,0.07,0.045),(0.15,0.065,0.045),(0.20,0.095,0.06),(0.26,0.23,0.19),(0.13,0.06,0.04)]): e.color=cc+(1.0,)
print("BRICK darker")
bpy.ops.wm.save_mainfile(); print("SAVED")
