# ws244 sky-speck check (SELF_REVIEW ws233 question): cast camera rays through the sky band of the ws244 eye WIP
# (CAM2, pixels x 100..480, y 110..160 of 704x396) in the same subset context and list what they hit.
import bpy, math, os
from mathutils import Vector
c=Vector((-326.0,96.0,135.3)); t=Vector((-232.0,100.0,136.2)); lens=28.0; W,H=704,396
f=(t-c).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
hw=18.0/lens; hh=hw*H/W
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
hits={}
for py in range(110,162,3):
    for px in range(100,482,4):
        sx=(px+0.5)/W*2-1; sy=1-(py+0.5)/H*2
        d=(f+r*sx*hw+u*sy*hh).normalized()
        ok,loc,nor,idx,ob,mx=sc.ray_cast(dg,c,d,distance=5000)
        if ok:
            k=ob.name; h=hits.setdefault(k,[0,loc.copy(),(loc-c).length]); h[0]+=1
out=['P244S %s n=%d at (%.0f,%.0f,%.1f) dist %.0f'%(k[:60],v[0],v[1].x,v[1].y,v[1].z,v[2]) for k,v in sorted(hits.items(),key=lambda kv:-kv[1][0])]
open('/workspace/nj-scenes/montclair-state/scripts/ws244/probe244b.out','w').write('\n'.join(out)); print('\n'.join(out[:40]),flush=True); os._exit(0)
