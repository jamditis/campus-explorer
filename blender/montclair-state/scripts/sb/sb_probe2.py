import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); cam=bpy.data.objects['SB_CAM_closeup_promenade_annex_W']
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]  # tr, br, bl, tl
o=cam.matrix_world.translation
for px,py in ((540,355),(650,360),(780,350),(600,330),(560,345),(700,340),(900,345)):
    u=px/1024; v=py/576
    top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); p=top.lerp(bot,v)
    r=sc.ray_cast(dg,o,(p-o).normalized())
    print('P2',px,py,r[4].name if r[0] else None, tuple(round(c,2) for c in r[1]) if r[0] else '')
