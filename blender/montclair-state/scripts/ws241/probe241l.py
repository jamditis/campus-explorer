# which surfaces make the remaining dark lines in the W57 eye view (camera -348,-64,120.3 -> -352,0,121.6, 28 mm, 704x396)
import bpy, os, math
from mathutils import Vector
for o in bpy.data.objects:
    for m in o.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
E=Vector((-348,-64,120.3)); T=Vector((-352,0,121.6)); f=(T-E).normalized()
r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
W,H=704,396; fw=36/28.0
out=[]
for (px,py) in [(100,240),(200,233),(300,226),(50,312),(100,300),(150,290),(30,258),(330,230),(250,262)]:
    for dy in (-3,0,3):
        sx=(px+0.5)/W-0.5; sy=0.5-(py+dy+0.5)/H
        d=(f+r*(sx*fw)+u*(sy*fw*H/W)).normalized()
        h=sc.ray_cast(dg,E,d,distance=500)
        out.append('px %d,%d -> %s at %s n=%s'%(px,py+dy,h[4].name[:40] if h[0] else None,tuple(round(c,2) for c in h[1]) if h[0] else '',tuple(round(c,2) for c in h[2]) if h[0] else ''))
open('/workspace/nj-scenes/montclair-state/scripts/ws241/probe241l.out','w').write('\n'.join(out)); print('P241L ok',flush=True); os._exit(0)
