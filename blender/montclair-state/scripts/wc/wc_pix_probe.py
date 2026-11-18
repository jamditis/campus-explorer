import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); cam=bpy.data.objects['WC_CAM_closeup_436_north_end_from_SE']
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]  # tr, br, bl, tl
P=cam.matrix_world.translation; W,H=1024,576
def ray(px,py):
    u=px/W; v=py/H
    top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); t=top.lerp(bot,v); return (t-P).normalized()
for px,py in [(500,350),(520,353),(560,360),(600,366),(640,372),(150,272),(200,285),(250,296),(240,292)]:
    for dy in (-2,0,2):
        d=ray(px,py+dy); h=sc.ray_cast(dg,P,d)
        print(px,py+dy, h[4].name[:30] if h[0] else None, tuple(round(c,2) for c in h[1]) if h[0] else '', tuple(round(c,2) for c in h[2]) if h[0] else '')
