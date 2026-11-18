import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); cam=bpy.data.objects['WA2_CAM_eye_richardson_west_walk_from_W']
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]  # tr, br, bl, tl
P=cam.matrix_world.translation; W,H=1024,576
def ray(px,py):
    u=px/W; v=py/H
    top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); t=top.lerp(bot,v); return (t-P).normalized()
for px,py in [(60,405),(120,430),(180,460),(250,500),(320,545),(140,440),(200,470)]:
    for dy in (-2,0,2):
        d=ray(px,py+dy); h=sc.ray_cast(dg,P,d)
        print(px,py+dy, h[4].name[:30] if h[0] else None, tuple(round(c,2) for c in h[1]) if h[0] else '', tuple(round(c,2) for c in h[2]) if h[0] else '')
