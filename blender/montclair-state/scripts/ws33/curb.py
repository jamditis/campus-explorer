# ws33: dock-drive granite curb sat ~0.30 m proud of the drive (CurbSweep profile = point-0.15..point+0.30) and was buried/humped on the west line.
# Re-seat curb points in the dock box so the curb top = drive surface + 0.15 m, smoothed along the line.
import bpy
from mathutils import Vector
c=bpy.data.objects['Curbs_granite_OSM']; m=c.matrix_world; mi=m.inverted()
dg=bpy.context.evaluated_depsgraph_get()
R=bpy.data.objects['Roads_OSM'];T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def rz(o,x,y):
    e=o.evaluated_get(dg); oi=o.matrix_world.inverted()
    ok,hp,_,_=e.ray_cast(oi@Vector((x,y,200)),(oi.to_3x3()@Vector((0,0,-1))).normalized())
    return (o.matrix_world@hp).z if ok else None
X0,X1,Y0,Y1=-12,10,-62,-14
REVEAL=0.15; TOPOFF=0.30
tot=0
for si in (1,2):
    sp=c.data.splines[si]; P=list(sp.points)
    W=[m@Vector(p.co[:3]) for p in P]
    idx=[i for i,w in enumerate(W) if X0<w.x<X1 and Y0<w.y<Y1]
    if not idx: continue
    tgt={}
    for i in idx:
        w=W[i]; rs=[]
        for dx,dy in ((1,0),(-1,0),(0,-1),(0,1),(0.6,0),(-0.6,0)):
            z=rz(R,w.x+dx,w.y+dy)
            if z is not None and abs(z-w.z)<1.0: rs.append(z)
        if rs: tgt[i]=max(rs)+REVEAL-TOPOFF
    # fill gaps by interpolation, then smooth 2 passes
    ks=sorted(tgt)
    for i in idx:
        if i not in tgt:
            lo=[k for k in ks if k<i]; hi=[k for k in ks if k>i]
            if lo and hi:
                a,b=lo[-1],hi[0]; t=(i-a)/(b-a); tgt[i]=tgt[a]*(1-t)+tgt[b]*t
    for _ in range(2):
        nt=dict(tgt)
        for i in tgt:
            nb=[tgt[j] for j in (i-1,i,i+1) if j in tgt]; nt[i]=sum(nb)/len(nb)
        tgt=nt
    for i,z in tgt.items():
        # taper at the box ends (first/last 2 points blend 1/3, 2/3)
        k=min(abs(i-min(tgt)),abs(max(tgt)-i)); f=min(1.0,(k+1)/3.0)
        w=W[i]; nz=w.z*(1-f)+z*f
        n=mi@Vector((w.x,w.y,nz)); P[i].co=(n.x,n.y,n.z,P[i].co[3]); tot+=1
        print('S',si,round(w.x,2),round(w.y,2),'%.2f -> %.2f'%(w.z,nz))
c.data.update_tag(); c.update_tag(); print('curb pts reseated',tot)
