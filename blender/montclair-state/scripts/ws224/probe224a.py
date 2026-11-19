# ws224: evaluated camera-ray probe (object code, face index, z, normal z) on a pixel grid of a subset camera
import bpy,os,sys
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
c=[float(s) for s in os.environ['PCAM'].split(',')]
E=Vector(c[:3]); T=Vector(c[3:6]); lens=c[6]; W,H=704,396
f=(T-E).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
X0,X1,SX,Y0,Y1,SY=[int(s) for s in os.environ['PX'].split(',')]
codes={}
for py in range(Y0,Y1+1,SY):
    row=[]
    for px in range(X0,X1+1,SX):
        a=(px+0.5)/W-0.5; b=0.5-(py+0.5)/H
        d=(f+r*(a*36/lens)+u*(b*36/lens*H/W)).normalized()
        o=E.copy(); res='----'
        for _ in range(6):
            h,loc,n,i,ob,m=sc.ray_cast(dg,o,d)
            if not h: break
            if ob.hide_render: o=loc+d*1e-3; continue
            k=ob.name[:30]
            if k not in codes: codes[k]=chr(65+len(codes))
            res='%s%d:%.3f:%+.2f'%(codes[k],i,loc.z,n.z); break
        row.append(res)
    print('P224 y%03d '%py+' '.join(row))
for k,v in codes.items(): print('P224 code',v,k)
sys.stdout.flush(); os._exit(0)
