import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=Vector((-228.0,-108.0,128.2)); tgt=Vector((-236.0,-99.0,124.2)); fl=28.0
q=(tgt-cam).to_track_quat('-Z','Y'); W,H=640,360; sw=36.0; sh=sw*H/W
for (px,py) in [(120,322),(125,325),(130,328),(125,332),(138,334),(140,338),(142,342),(136,340),(400,203),(405,205),(410,207),(405,212),(350,236),(300,232)]:
    x=(px/W-0.5)*sw; y=(0.5-py/H)*sh
    d=q@Vector((x,y,-fl)); d.normalize(); o0=cam.copy()
    for _ in range(6):
        r=sc.ray_cast(dg,o0,d)
        if not r[0] or not r[4].hide_render: break
        o0=r[1]+d*0.0005
    print('R203c',px,py,r[4].name[:30] if r[0] else None, tuple(round(c,4) for c in r[1]) if r[0] else None, tuple(round(c,3) for c in r[2]) if r[0] else None,flush=True)
