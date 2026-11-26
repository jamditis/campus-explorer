# ws248 W62g pass 1 (standalone, on ws248b): LiDAR ground patch E of the east stand + the back walk re-draped on it.
# PB_terrain_fan_regrid left NO vertices in x -220..-185, y 60..130 (big fan triangles), so the GN snap (f248b) can only fix
# their corner verts. The patch = 1 m LiDAR grid (2023, 2017 fallback, 3x3 mean) +2 cm, cells under the stand pad (+0.3 m)
# left out, 0.6 m skirts on open edges; 'ortho' UV from an affine fit of the terrain's own 'ortho' UV (same imagery).
import bpy, os, sys, json, numpy as np, warnings; warnings.filterwarnings('ignore')
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws248b.blend')
WN='WS247_E_stand_back_walk_ortho2020_UNVERIFIED_level'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','fse_stand_under_pad','Footpaths_OSM',WN,'fse_front_walkway','fse_stand_entry_steps','fse_press_box']
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T,PAD,FP,WK=b.objects[:4]
for m in T.modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,box=(-250,-180,35,145)):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    t=BVHTree.FromPolygons(vs,ps) if ps else None; e.to_mesh_clear(); return t
PB=bvh(PAD); OB=[bvh(o) for o in b.objects[4:]]
def hit(t,x,y):
    if t is None: return None
    h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return None if h[0] is None else h[0].z
# --- terrain UV affine fit + material slot used there
me=T.data; M=T.matrix_world; uvl=me.uv_layers['ortho'].data; P=[];U=[];mi=[]
for p in me.polygons:
    c=M@p.center
    if -260<c.x<-170 and 20<c.y<170:
        mi.append(p.material_index)
        for li in p.loop_indices:
            w=M@me.vertices[me.loops[li].vertex_index].co; P.append((w.x,w.y)); U.append(tuple(uvl[li].uv))
P=np.array(P);U=np.array(U);X=np.c_[P,np.ones(len(P))];A=np.linalg.lstsq(X,U,rcond=None)[0]
res=np.abs(X@A-U).max(); from collections import Counter; mslot=Counter(mi).most_common(1)[0][0]
print('H248P uv fit maxres',round(float(res),6),'mat slot',mslot,me.materials[mslot].name if me.materials[mslot] else None,flush=True)
# --- LiDAR grid
G23=np.load('/workspace/nj-scenes/montclair-state/scripts/ws248/g1m_23.npy'); G17=np.load('/workspace/nj-scenes/montclair-state/scripts/ws248/g1m_17.npy')
G=np.where(np.isfinite(G23),G23,G17); X0,Y0=-320.,-20.
def nb(G,r):
    ny,nx=G.shape; pad=np.pad(G,r,constant_values=np.nan); return np.stack([pad[r+dy:r+dy+ny,r+dx:r+dx+nx] for dy in range(-r,r+1) for dx in range(-r,r+1)])
for r in (1,2,3): G=np.where(np.isfinite(G),G,np.nanmedian(nb(G,r),axis=0))
Gs=np.nanmean(nb(G,1),axis=0)
def gz(x,y):  # bilinear on cell centres (cell i covers [X0+i, X0+i+1))
    fx=x-X0-0.5; fy=y-Y0-0.5; i=int(np.floor(fx)); j=int(np.floor(fy)); tx=fx-i; ty=fy-j
    q=Gs[j:j+2,i:i+2]; return float(q[0,0]*(1-tx)*(1-ty)+q[0,1]*tx*(1-ty)+q[1,0]*(1-tx)*ty+q[1,1]*tx*ty)
XA,XB,YA,YB=float(os.environ.get('XA','-226')),-186.,44.,136.
xs=np.arange(XA,XB+0.01,1.0); ys=np.arange(YA,YB+0.01,1.0)
def under_pad(x,y):
    for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
        if hit(PB,x+dx,y+dy) is not None: return True
    for t in OB:
        if hit(t,x,y) is not None: return True
    return False
V=[];idx={}
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        z=gz(x,y)
        if not np.isfinite(z): continue
        idx[(i,j)]=len(V); V.append([float(x),float(y),z+0.02])
Fq=[]
for j in range(len(ys)-1):
    for i in range(len(xs)-1):
        q=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if not all(k in idx for k in q): continue
        cx=xs[i]+0.5; cy=ys[j]+0.5
        if under_pad(cx,cy) or any(under_pad(V[idx[k]][0],V[idx[k]][1]) for k in q): continue
        Fq.append([idx[k] for k in q])
# skirts on open (boundary) edges
from collections import defaultdict
ec=defaultdict(int)
for f in Fq:
    for k in range(4): ec[tuple(sorted((f[k],f[(k+1)%4])))]+=1
bnd={}
for f in Fq:
    for k in range(4):
        a,b_=f[k],f[(k+1)%4]
        if ec[tuple(sorted((a,b_)))]==1: bnd[(a,b_)]=1
low={}
def lowv(a):
    if a not in low: low[a]=len(V); V.append([V[a][0],V[a][1],V[a][2]-0.6])
    return low[a]
NF=len(Fq)
for (a,b_) in bnd: Fq.append([b_,a,lowv(a),lowv(b_)])
UV=[list(map(float,np.array([v[0],v[1],1.0])@A)) for v in V]
print('H248P patch verts',len(V),'faces top',NF,'skirt',len(Fq)-NF,'z',round(min(v[2] for v in V[:len(idx)]),2),round(max(v[2] for v in V[:len(idx)]),2),flush=True)
# --- walk re-drape on the LiDAR surface (same plan as h247: ortho trace, 2.8 m, 5 cm off the pad, level across)
TR=[(52,-232.2),(54,-231.6),(57,-230.75),(60,-230.0),(63,-229.5),(66,-228.75),(69,-228.1),(72,-227.4),(75,-226.75),(78,-226.1),(81,-225.25),(84,-224.75),(86,-224.5),(89,-224.1),(92,-223.1),(95,-222.4),(98,-221.75),(101,-221.25),(104,-220.25),(107,-219.75),(110,-219.1),(113,-218.4),(116,-217.75),(119,-217.1),(122,-216.6),(125,-216.0),(128,-215.75),(131,-215.75),(134,-215.75),(137,-215.75),(140,-215.75),(143,-215.85),(146,-215.85),(149,-215.85),(152,-215.85),(154,-215.4)]
ty=np.array([p[0] for p in TR],float); tx=np.array([p[1] for p in TR],float); txs=np.convolve(np.pad(tx,2,mode='edge'),np.ones(5)/5,'valid')
FB=bvh(FP); Wd=2.8; wys=np.arange(52,154.01,0.5); cx=np.interp(wys,ty,txs)
def padE(y):
    for x in np.arange(-212,-246,-0.1):
        if hit(PB,x,y) is not None: return x
    return None
rows=[];lo=[]
for i,y in enumerate(wys):
    j0=max(i-1,0); j1=min(i+1,len(wys)-1); d=np.array([cx[j1]-cx[j0],wys[j1]-wys[j0]]); d/=np.linalg.norm(d); n=np.array([d[1],-d[0]])
    c=np.array([cx[i],y]); pe=padE(y)
    if pe is not None and (c-n*Wd/2)[0]<pe+0.05: c=c+n*((pe+0.05)-(c-n*Wd/2)[0])/n[0]
    r=[]
    for a in (-0.5,-1/6,1/6,0.5):
        p=c+n*Wd*a; zz=gz(p[0],p[1])
        zf=hit(FB,p[0],p[1])
        if zf is not None and y>148: zz=max(zz,zf)   # meet the OSM path at the University Hall end
        r.append([p[0],p[1],zz+0.05])
    g=[q[2] for q in r]; lo.append(min(g)-0.05)
    for q in r: q[2]=max(g)
    rows.append(r)
R=np.array(rows); Zt=R[:,:,2].copy()
for it in range(3):
    Zs=Zt.copy(); Zs[1:-1]=(Zt[:-2]+Zt[1:-1]+Zt[2:])/3; Zt=np.maximum(Zs,R[:,:,2]-0.02)
R[:,:,2]=Zt; LO=np.array(lo); WV=[];WF=[]
for k,r in enumerate(R):
    for p in r: WV.append(tuple(map(float,p)))
    WV.append((float(r[0][0]),float(r[0][1]),float(min(r[0][2]-0.15,LO[k]-0.05)))); WV.append((float(r[-1][0]),float(r[-1][1]),float(min(r[-1][2]-0.15,LO[k]-0.05))))
for i in range(len(R)-1):
    a=i*6; b_=(i+1)*6
    for q in range(3): WF.append((a+q,a+q+1,b_+q+1,b_+q))
    WF.append((a+4,a,b_,b_+4)); WF.append((a+3,a+5,b_+5,b_+3))
dr=(R[:,:,2].max(1)-LO)
print('H248P walk rows',len(R),'z',round(R[:,:,2].min(),2),round(R[:,:,2].max(),2),'max edge drop',round(float(dr.max()),2),'rows drop>0.3',int((dr>0.3).sum()),flush=True)
for y in (52,70,90,110,130,150):
    i=int((y-52)/0.5); pz=hit(PB,R[i,0,0]-0.3,y); print('H248P y',y,'walk z',round(R[i,0,2],3),'pad z W of walk',None if pz is None else round(pz,2),flush=True)
json.dump({'V':V,'F':Fq,'UV':UV,'mslot':mslot,'WV':WV,'WF':WF},open('/workspace/nj-scenes/montclair-state/scripts/ws248/h248p.json','w'))
sys.stdout.flush(); os._exit(0)
