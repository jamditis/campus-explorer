import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=Vector((-293.0,-238.6,119.9)); tgt=Vector((-308.0,-236.0,117.9)); fl=26.0
q=(tgt-cam).to_track_quat('-Z','Y'); W,H=768,432; sw=36.0; sh=sw*H/W
for (px,py) in [(360,284),(380,280),(380,286),(380,292),(400,276),(400,284),(420,272),(420,280),(345,292),(440,262)]:
    x=(px/W-0.5)*sw; y=(0.5-py/H)*sh
    d=q@Vector((x,y,-fl)); d.normalize(); o0=cam.copy()
    for _ in range(6):
        r=sc.ray_cast(dg,o0,d)
        if not r[0] or not r[4].hide_render: break
        o0=r[1]+d*0.0005
    print('R203c',px,py,r[4].name[:30] if r[0] else None, tuple(round(c,4) for c in r[1]) if r[0] else None, tuple(round(c,3) for c in r[2]) if r[0] else None,flush=True)
