import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=bpy.data.objects['PU_CAM_closeup_dickson_west_windows']; dg=bpy.context.evaluated_depsgraph_get()
W,H=640,360; sc.render.resolution_x=1920; sc.render.resolution_y=1080
fr=cam.data.view_frame(scene=sc); fr=[cam.matrix_world@v for v in fr]  # tr,br,bl,tl
tr,br,bl,tl=fr
for px,py in [(530,232),(385,252),(300,88),(150,150),(250,113),(420,40),(100,170)]:
    fx=px/W; fy=py/H
    top=tl+(tr-tl)*fx; bot=bl+(br-bl)*fx; p=top+(bot-top)*fy
    d=(p-cam.matrix_world.translation).normalized()
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,cam.matrix_world.translation,d)
    mn=None
    if hit and ob.type=='MESH':
        me=ob.data; mi=me.polygons[idx].material_index if idx<len(me.polygons) else -1
        mn=ob.material_slots[mi].material.name if mi<len(ob.material_slots) and ob.material_slots[mi].material else None
    print('RAY',px,py,hit and ob.name[:60],idx,mn,tuple(round(x,2) for x in loc) if hit else None)
