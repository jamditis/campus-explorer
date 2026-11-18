import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
for o in bpy.data.objects:
    if o.hide_render: continue
    lo,hi=bb(o)
    if hi[0]>-21 and lo[0]<-8 and hi[1]>5 and lo[1]<11.5 and lo[2]<138.2 and hi[2]>137.3 and (hi[2]-lo[2])<1.6 and (hi[1]-lo[1])<1.5:
        print('B2|%s|%s|%s|%s|%s|%s'%(o.name,o.type,[round(v,2) for v in lo],[round(v,2) for v in hi],[s.material.name if s.material else None for s in o.material_slots],[c.name for c in o.users_collection]))

sc=bpy.context.scene; cam=bpy.data.objects.get('NI_CAM_closeup_front_doors_straight')
dg=bpy.context.evaluated_depsgraph_get(); cd=cam.data; M=cam.matrix_world
fr=[M@v for v in cd.view_frame(scene=sc)]
from collections import Counter
C=Counter()
for i in range(15):
  for j in range(15):
    u=0.74+0.09*i/14; v=0.08+0.2*j/14
    p=fr[2]+(fr[1]-fr[2])*u+(fr[3]-fr[2])*v
    d=(p-M.translation).normalized(); o=M.translation
    for k in range(8):
        hit,loc,n,ii,ob,_=sc.ray_cast(dg,o,d)
        if not hit: break
        if 'glass' not in ob.name.lower(): C[(ob.name,round(loc.x,1),round(loc.y,1),round(loc.z,1))]+=1; break
        o=loc+d*0.002
for k,c in C.most_common(30): print('HIT',c,k)
