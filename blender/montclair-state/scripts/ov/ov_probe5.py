import bpy, mathutils
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['OT_CAM_aerial_north_strip_CELS_Calcia']
print('CAM',tuple(round(v,2) for v in cam.location), cam.data.lens, cam.parent)
sc.camera=cam
fr=cam.data.view_frame(scene=sc); M=cam.matrix_world
def ray(u,v):
    # u,v in 0..1 from top-left
    tr,br,bl,tl=[M@p for p in fr]
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v)
    o=M.translation; d=(p-o).normalized()
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,o,d)
    return hit,loc,nor,idx,ob,(loc-o).length if hit else None
for (px,py) in [(100,238),(250,240),(400,243),(250,232),(250,250),(300,262),(820,262),(200,270)]:
    h,l,n,i,ob,dist=ray(px/1024,py/576)
    print('PX',px,py, ob.name if h else None, tuple(round(c,2) for c in l) if h else None, tuple(round(c,2) for c in n) if h else None, round(dist,2) if h else None, i)
