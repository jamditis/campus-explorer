import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=Vector((-313.0,-239.0,118.6)); tgt=Vector((-292.0,-236.0,118.3)); fl=26.0
q=(tgt-cam).to_track_quat('-Z','Y'); W,H=768,432; sw=36.0; sh=sw*H/W
for (px,py) in [(400,328),(400,334),(400,340),(480,345),(480,350),(480,356),(560,358),(560,364),(560,370),(660,380),(660,388),(660,396)]:
    x=(px/W-0.5)*sw; y=(0.5-py/H)*sh
    d=q@Vector((x,y,-fl)); d.normalize(); r=sc.ray_cast(dg,cam,d)
    print('R203b',px,py,r[4].name[:30] if r[0] else None, tuple(round(c,3) for c in r[1]) if r[0] else None, tuple(round(c,3) for c in r[2]) if r[0] else None,flush=True)
