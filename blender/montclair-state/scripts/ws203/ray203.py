import bpy, math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=Vector((-306.5,-237.6,118.75)); tgt=Vector((-302.1,-236.4,118.2)); fl=35.0
q=(tgt-cam).to_track_quat('-Z','Y'); W,H=768,432; sw=36.0; sh=sw*H/W
for (px,py) in [(380,270),(380,276),(380,282),(380,290),(330,276),(330,284),(440,272),(440,280),(500,240),(520,215),(625,180),(632,180),(640,180),(200,370),(230,400)]:
    x=(px/W-0.5)*sw; y=(0.5-py/H)*sh
    d=q@Vector((x,y,-fl)); d.normalize()
    r=sc.ray_cast(dg,cam,d)
    print('R203',px,py,r[4].name[:40] if r[0] else None, tuple(round(c,3) for c in r[1]) if r[0] else None, tuple(round(c,2) for c in r[2]) if r[0] else None,flush=True)
