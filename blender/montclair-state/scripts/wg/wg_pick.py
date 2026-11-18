import bpy
from mathutils import Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d
sc=bpy.context.scene; O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
cam=O['WF_CAM_closeup_436_east_edge']; sc.render.resolution_x=1280; sc.render.resolution_y=720
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl
mw=cam.matrix_world
def ray(u,v):
    tl,tr,bl=fr[3],fr[0],fr[2]
    p=tl+(tr-tl)*u+(bl-tl)*v
    return mw.translation,(mw@p-mw.translation).normalized()
for (u,v,tag) in [(250/1024,230/576,'blotch1'),(300/1024,260/576,'blotch2'),(200/1024,200/576,'blotch3'),(450/1024,400/576,'clean')]:
    o,d=ray(u,v); start=o
    for k in range(4):
        hit,loc,nor,idx,ob,_=sc.ray_cast(dg,start,d)
        if not hit: break
        mat=ob.material_slots[ob.data.polygons[idx].material_index].material.name if ob.type=='MESH' and ob.material_slots else None
        print('PICK',tag,k,ob.name,tuple(round(c,3) for c in loc),mat,flush=True)
        start=loc+d*0.002
