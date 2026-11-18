import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
for o in bpy.data.objects:
    if o.hide_render: continue
    lo,hi=bb(o)
    if hi[0]>-21 and lo[0]<-8 and hi[1]>5 and lo[1]<11.5 and lo[2]<138.2 and hi[2]>137.3 and (hi[2]-lo[2])<1.6 and (hi[1]-lo[1])<1.5:
        print('B2|%s|%s|%s|%s|%s|%s'%(o.name,o.type,[round(v,2) for v in lo],[round(v,2) for v in hi],[s.material.name if s.material else None for s in o.material_slots],[c.name for c in o.users_collection]))
# ray from closeup camera toward the bin pixel
sc=bpy.context.scene; cam=bpy.data.objects.get('NI_CAM_closeup_front_doors_straight')
from bpy_extras.view3d_utils import region_2d_to_vector_3d
dg=bpy.context.evaluated_depsgraph_get()
import math
cd=cam.data; M=cam.matrix_world
fr=[M@v for v in cd.view_frame(scene=sc)]
for u,v in ((0.90,0.06),(0.89,0.04),(0.885,0.07)):
    # frame: 0 tr,1 br,2 bl,3 tl
    p=fr[2]+(fr[1]-fr[2])*u+(fr[3]-fr[2])*v
    d=(p-M.translation).normalized(); o=M.translation
    for k in range(6):
        hit,loc,n,i,ob,_=sc.ray_cast(dg,o,d)
        if not hit: break
        print('RAY',u,v,ob.name,[round(x,2) for x in loc])
        o=loc+d*0.002
