# W60: which surfaces form the dark saw-tooth at the Lot 28S W edge in the ws241 oblique (camera from jobwip241 CAM1)
import bpy, os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
c=[float(v) for v in os.environ.get('PCAM','-262.0,528.0,168.0,-112.0,655.0,113.0,30').split(',')]
E=Vector(c[0:3]); T=Vector(c[3:6]); fl=c[6]; f=(T-E).normalized()
r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f); W,H=704,396; fw=36/fl; out=[]
x0,x1,xs,y0,y1,ys=[int(v) for v in os.environ.get('PGRID','0,90,3,250,396,6').split(',')]
for py in range(y0,y1,ys):
    row=[]
    for px in range(x0,x1,xs):
        sx=(px+0.5)/W-0.5; sy=0.5-(py+0.5)/H
        d=(f+r*(sx*fw)+u*(sy*fw*H/W)).normalized(); h=sc.ray_cast(dg,E,d,distance=1500)
        up=sc.ray_cast(dg,h[1]+Vector((0,0,0.02)),Vector((0,0,1)),distance=30) if h[0] else (False,)
        row.append(('%d:%s@%.1f,%.1f,%.2f n%.2f'%(px,h[4].name[:22],h[1].x,h[1].y,h[1].z,h[2].z)+(' UNDER %s@%.2f'%(up[4].name[:14],up[1].z) if up[0] else '')) if h[0] else '%d:MISS'%px)
    out.append('py %d | '%py+' ; '.join(row))
open('/workspace/nj-scenes/montclair-state/scripts/ws242/'+os.environ.get('PO','probe242c.out'),'w').write('\n'.join(out)); print('P242C ok',flush=True); os._exit(0)
