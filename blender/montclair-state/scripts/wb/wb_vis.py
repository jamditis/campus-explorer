import bpy, json
from mathutils import Vector
O=Vector((229.624,391.68,0));U=Vector((0.3338,0.9426,0));N=Vector((-0.9426,0.3338,0))
P=lambda t,n,z: O+U*t+N*n+Vector((0,0,z))
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
pts=[P(t,0.9,z) for t in (-7,-4,-1,2) for z in (124,130,135,138,142,148,155)]
cands=[(0,15,146),(0,12,140),(-2,16,150),(3,14,152),(-5,13,138),(10,30,165),(20,25,160),(0,40,175),(-4,60,180),(15,45,170),(25,40,150),(8,10,145)]
for c in cands:
    cp=P(*c); vis=0
    for p in pts:
        d=(p-cp); L=d.length; hit=sc.ray_cast(dg,cp,d.normalized(),distance=L-0.6)
        if not hit[0] or (hit[4] and hit[4].name.startswith(('WB_','VW_','WA_'))): vis+=1
    inside=sc.ray_cast(dg,cp,Vector((0,0,1)))
    print('VIS',c,'%d/%d'%(vis,len(pts)),'up-hit',inside[4].name if inside[0] else None, [round(a,2) for a in cp])
