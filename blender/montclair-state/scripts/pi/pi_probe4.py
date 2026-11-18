import bpy
from mathutils import Vector
s=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['PF_CAM_closeup_feliciano_entrance']; s.render.resolution_x=1024; s.render.resolution_y=576
tr,br,bl,tl=[cam.matrix_world@v for v in cam.data.view_frame(scene=s)]; o=cam.matrix_world.translation
for px,py in [(380,427),(640,427),(380,155),(200,345)]:
    u=px/1024; v=py/576; top=tl+(tr-tl)*u; bot=bl+(br-bl)*u; p=top+(bot-top)*v
    hit,loc,nor,idx,ob,_=s.ray_cast(dg,o,(p-o).normalized())
    e=ob.evaluated_get(dg); me=e.to_mesh(); print('RAY',px,py,ob.name,[round(x,2) for x in loc],e.material_slots[me.polygons[idx].material_index].material.name)
w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world; R=mw.to_3x3()
for p in w.data.polygons:
    n=(R@p.normal).normalized()
    if n.x>0.9:
        vs=[mw@w.data.vertices[v].co for v in p.vertices]
        print('E',p.index,round(min(v.x for v in vs),2),round(min(v.y for v in vs),1),round(max(v.y for v in vs),1),round(min(v.z for v in vs),1),round(max(v.z for v in vs),1),[round(x,2) for x in n])
c=bpy.data.objects['PF_CAM_eye_feliciano_east']; print('CAM',[round(x,1) for x in c.location],[round(x,2) for x in c.rotation_euler])
