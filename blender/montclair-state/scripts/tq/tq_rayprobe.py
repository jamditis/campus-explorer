import bpy, os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects[os.environ['CAM']]; W,H=int(os.environ.get('W',768)),int(os.environ.get('H',432))
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl in cam space
tr,br,bl,tl=[cam.matrix_world@v for v in fr]; o=cam.matrix_world.translation
for px,py in [tuple(map(int,p.split(','))) for p in os.environ['PIX'].split(';')]:
    u=px/W; v=py/H
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v); d=(p-o).normalized()
    hit,loc,nor,idx,ob,mw=sc.ray_cast(dg,o,d)
    print('RAY',px,py,hit,ob.name if ob else None,[round(c,2) for c in loc],idx)
