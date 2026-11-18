import bpy
from mathutils import Vector
s=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['PF_CAM_eye_feliciano_east']; s.render.resolution_x=1024; s.render.resolution_y=576
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=s)]  # tr, br, bl, tl
tr,br,bl,tl=fr; o=cam.matrix_world.translation
for px,py in [(500,395),(200,400),(800,370),(500,250)]:
    u=px/1024; v=py/576
    top=tl+(tr-tl)*u; bot=bl+(br-bl)*u; p=top+(bot-top)*v
    d=(p-o).normalized(); hit,loc,nor,idx,ob,_=s.ray_cast(dg,o,d)
    mat=None
    if hit and ob.type=='MESH':
        e=ob.evaluated_get(dg); me=e.to_mesh()
        try: mat=e.material_slots[me.polygons[idx].material_index].material.name if e.material_slots else None
        except Exception as ex: mat=str(ex)
    print('RAY',px,py,hit and ob.name,[round(x,1) for x in loc] if hit else None,[round(x,2) for x in nor] if hit else None,idx,mat)
