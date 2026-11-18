# ws90: straighten College Ave WS27 carriageway + both curbs (Joe 12:10 PM: wobbly curb/ground lines)
import bpy,math,os,statistics as st
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects; N=281
CW=OB['WS27_CollegeAve_carriageway_2020ortho']; CR=OB['WS27_CollegeAve_curb_right_UNVERIFIED']; CL=OB['WS27_CollegeAve_curb_left_UNVERIFIED']
SX=int(os.environ.get('SXY','4')); SZ=int(os.environ.get('SZ','6')); CLAMP=float(os.environ.get('CLAMP','0.25'))
def W(o): mw=o.matrix_world; return [mw@v.co for v in o.data.vertices]
def gs(a,s):
    out=[]
    for i in range(len(a)):
        w=t=0
        for j in range(max(0,i-3*s),min(len(a),i+3*s+1)):
            g=math.exp(-((i-j)/s)**2/2); w+=g; t+=g*a[j]
        out.append(t/w)
    return out
CZ=[]
def bvh_ws(objs):
    P=[];F=[]
    for o in objs:
        b=len(P); P+= W(o); F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    bv=BVHTree.FromPolygons(P,F); CZ.append([sum(P[i].z for i in f)/len(f) for f in F]); return bv
C=W(CW); R=W(CR); L=W(CL)
OLD=bvh_ws([CW,CR,CL])
# terrain
T=OB['Terrain_LiDAR_DTM_1m']; e=T.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=e.to_mesh()
TB=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear()
def tz(x,y):
    h=TB.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] else -1e9
sec=lambda V,k,i: V[i*k:(i+1)*k]
# centreline + frame
cx=[sec(C,7,i)[3].x for i in range(N)]; cy=[sec(C,7,i)[3].y for i in range(N)]
sx,sy=gs(cx,SX),gs(cy,SX)
tan=[];nor=[]
for i in range(N):
    a=max(0,i-1);b=min(N-1,i+1); t=Vector((sx[b]-sx[a],sy[b]-sy[a],0)).normalized(); tan.append(t)
    n=Vector((t.y,-t.x,0))
    # orient toward right edge (col0)
    if n.dot(sec(C,7,i)[0]-sec(C,7,i)[3])<0: n=-n
    nor.append(n)
# lateral coords of carriageway cols relative to raw centre along normal
lat=[[ (sec(C,7,i)[k]-sec(C,7,i)[3]).dot(nor[i]) for k in range(7)] for i in range(N)]
hr=gs([lat[i][0] for i in range(N)],SZ*2); hl=gs([-lat[i][6] for i in range(N)],SZ*2)
frac=[st.median([lat[i][k]/(lat[i][0] if k<3 else -lat[i][6]) if k!=3 else 0 for i in range(N)]) for k in range(7)]
# z
zc=gs([sec(C,7,i)[3].z for i in range(N)],SZ)
dR=gs([sec(C,7,i)[0].z-sec(C,7,i)[3].z for i in range(N)],SZ*2); dL=gs([sec(C,7,i)[6].z-sec(C,7,i)[3].z for i in range(N)],SZ*2)
dR=[max(-0.15,min(0.05,v)) for v in dR]; dL=[max(-0.15,min(0.05,v)) for v in dL]
newC=[]
for i in range(N):
    c0=Vector((sx[i],sy[i],0))
    for k in range(7):
        if k<3: f=frac[k]; off=f*hr[i]; z=zc[i]+dR[i]*abs(f)
        elif k==3: off=0; z=zc[i]
        else: f=frac[k]; off=f*hl[i]; z=zc[i]+dL[i]*abs(f)
        p=c0+nor[i]*off; old=sec(C,7,i)[k]
        d=Vector((p.x-old.x,p.y-old.y,0))
        if d.length>CLAMP: p=Vector((old.x,old.y,0))+d.normalized()*CLAMP
        z=max(z,min(old.z,tz(p.x,p.y)+0.03))
        if os.environ.get('NOLOWER')=='1': z=min(max(z,old.z),old.z+float(os.environ.get('RAISEMAX','0.1')))
        newC.append(Vector((p.x,p.y,z)))
TAP=8
for i in range(N):
    w=1.0
    if i<TAP: w=(i/TAP)**2*(3-2*i/TAP)
    if N-1-i<TAP: j=N-1-i; w=min(w,(j/TAP)**2*(3-2*j/TAP))
    for k in range(7):
        o=sec(C,7,i)[k]; newC[i*7+k]=o+(newC[i*7+k]-o)*w
# curb template (lateral offset outward, dz) from col0
def tmpl(V,edgecol,sign):
    ofs=[[],[]]
    res=[]
    for k in range(6):
        res.append((st.median([ (sec(V,6,i)[k]-sec(V,6,i)[0]).dot(nor[i])*sign for i in range(N)]), st.median([sec(V,6,i)[k].z-sec(V,6,i)[0].z for i in range(N)])))
    return res
tR=tmpl(R,0,1); tL=tmpl(L,6,-1)
print('A90 frac',[round(f,3) for f in frac],'tR',[(round(a,3),round(b,3)) for a,b in tR],'tL',[(round(a,3),round(b,3)) for a,b in tL])
newR=[];newL=[]
for i in range(N):
    e0=newC[i*7+0]; e6=newC[i*7+6]
    for k in range(6):
        newR.append(e0+nor[i]*tR[k][0]+Vector((0,0,tR[k][1])))
        newL.append(e6-nor[i]*tL[k][0]+Vector((0,0,tL[k][1])))
# stats
dev=[(newC[j]-C[j]).length for j in range(len(C))]; dzz=[newC[j].z-C[j].z for j in range(len(C))]
big=[(j//7,j%7,round(dzz[j],2)) for j in range(len(C)) if abs(dzz[j])>0.1]; print('A90 bigdz',len(big),big[:60]); print('A90 road move max',round(max(dev),3),'dz',round(min(dzz),3),round(max(dzz),3))
def setw(o,P):
    inv=o.matrix_world.inverted()
    for v,p in zip(o.data.vertices,P): v.co=inv@p
    o.data.update()
setw(CW,newC); setw(CR,newR); setw(CL,newL)
for o in (CW,CR,CL):
    for p in o.data.polygons: p.use_smooth=False
NEW=bvh_ws([CW,CR,CL])
# reseat attached thin objects (paint etc.) by the z change
x0=min(p.x for p in C)-1;x1=max(p.x for p in C)+1;y0=min(p.y for p in C)-1;y1=max(p.y for p in C)+1
for o in OB:
    if o.type!='MESH' or o in (CW,CR,CL,T) or o.modifiers or o.hide_render or len(o.data.vertices)>40000 or len(o.data.vertices)==0: continue
    mw=o.matrix_world; inv=mw.inverted(); cnt=0
    bb=[mw@Vector(v) for v in o.bound_box]
    if max(v.x for v in bb)<x0 or min(v.x for v in bb)>x1 or max(v.y for v in bb)<y0 or min(v.y for v in bb)>y1: continue
    if o.data.users>1: continue
    for v in o.data.vertices:
        p=mw@v.co
        if not(x0<p.x<x1 and y0<p.y<y1): continue
        q,_,fi,d=OLD.find_nearest(p,0.6)
        if q is None: continue
        dz=CZ[1][fi]-CZ[0][fi]
        wt=1.0 if d<0.15 else max(0.0,1-(d-0.15)/0.45)
        dz*=wt
        if abs(dz)>0.002: v.co=inv@(p+Vector((0,0,dz))); cnt+=1
    if cnt: o.data.update(); print('A90 reseat',o.name[:50],cnt)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('A90 SAVED')
