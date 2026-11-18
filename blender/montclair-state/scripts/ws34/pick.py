import bpy,os
from mathutils import Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws34/camsonly.py').read())
bpy.context.view_layer.update()
c=bpy.data.objects[os.environ['CAM']]; sc.camera=c
sc.render.resolution_x=1280; sc.render.resolution_y=720
fr=c.data.view_frame(scene=sc)  # tr, br, bl, tl in camera space
tr,br,bl,tl=[c.matrix_world@v for v in fr]
for u,v in [tuple(map(float,s.split(':'))) for s in os.environ['PTS'].split(',')]:
    top=tl+(tr-tl)*u; bot=bl+(br-bl)*u; p=top+(bot-top)*v
    d=(p-c.matrix_world.translation).normalized()
    ok,loc,n,i,o,m=sc.ray_cast(dg,c.matrix_world.translation,d)
    print("PICK",tuple(round(x,1) for x in c.matrix_world.translation),tuple(round(x,2) for x in d),u,v,o.name if ok else '-',tuple(round(x,2) for x in loc) if ok else '')
