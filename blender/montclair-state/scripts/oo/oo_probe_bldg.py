import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=sc.objects['OO_CAM_eye_redraped_walk_N_of_schmitt']; sc.camera=cam
import bpy_extras
from mathutils import Matrix
fr=cam.data.view_frame(scene=sc)  # local corners
mw=cam.matrix_world
for u,v in [(a/20,b/20) for a in (15,17,19) for b in (12,13,14,16,18)]:
    # bilinear in frame: fr order tr, br, bl, tl
    tr,br,bl,tl=fr
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=bot.lerp(top,v)
    d=(mw.to_3x3()@p).normalized()
    hit,loc,n,i,o,m=sc.ray_cast(dg,mw.translation,d)
    print('HIT',u,v,hit,o.name if o else None,[round(x,1) for x in loc] if hit else None)
