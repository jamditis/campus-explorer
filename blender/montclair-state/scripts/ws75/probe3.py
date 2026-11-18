import bpy,os
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws75/camdef.py').read())
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['PROBECAM']; sc.render.resolution_x=704; sc.render.resolution_y=396
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]  # tr,br,bl,tl
tr,br,bl,tl=fr; o=cam.matrix_world.translation
for px,py in [(200,310),(150,340),(240,290),(330,240),(350,250),(130,240),(110,330),(260,300),(170,300),(230,220)]:
    u=px/704; v=py/396
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v)
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,o,(p-o).normalized())
    mat=''
    if hit and ob.type=='MESH':
        try: mat=ob.data.materials[ob.data.polygons[idx].material_index].name
        except Exception: pass
    print('HIT',(px,py),ob.name[:60] if hit else None,mat,tuple(round(c,1) for c in loc) if hit else '',flush=True)
