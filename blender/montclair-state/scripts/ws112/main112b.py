# ws112: UNIFY #11 E brick link walk, W branch walk y~-245 (ortho), UNIFY #12 Normal walk skirt, Roads_OSM under WS110 road, terrain cap
import bpy, bmesh, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
D=np.load(R+'prep/ws79_normal_ave_dtm/normal_ave_dtm_1m.npz'); DT=D['dtm']; DX0=float(D['x0']); DY0=float(D['y0'])
def dtm(x,y):
    fx=x-DX0; fy=y-DY0; j=int(np.floor(fx)); i=int(np.floor(fy))
    if not (0<=i<DT.shape[0]-1 and 0<=j<DT.shape[1]-1): return None
    a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
A=np.array([-244.8,-239.3]);B=np.array([-256.1,-271.6]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
def st(x,y): return (x-A[0])*d[0]+(y-A[1])*d[1],(x-A[0])*n[0]+(y-A[1])*n[1]
def W(s,t): p=A+d*s+n*t; return float(p[0]),float(p[1])
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
MAT=bpy.data.materials
M_conc=MAT.get('Paving_concrete'); M_brick=MAT['WS27_brick_crosswalk_2020ortho']
def bvh_of(o):
    me=o.data; mw=o.matrix_world
    return BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
pass
def link(name,bm,m):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob
fp=O('Footpaths_OSM'); bfp=bvh_of(fp)
def zfp(x,y):
    h=bfp.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); return None if h[0] is None else h[0].z
def ribbon(rows,name,m,skirt=0.30):
    # rows: list of list of (x,y,z) across width (>=2 pts each)
    bm=bmesh.new(); T=[[bm.verts.new(p) for p in r] for r in rows]
    L=[bm.verts.new((r[0][0],r[0][1],r[0][2]-skirt)) for r in rows]; Rr=[bm.verts.new((r[-1][0],r[-1][1],r[-1][2]-skirt)) for r in rows]
    k=len(rows[0])
    for i in range(len(rows)-1):
        for j in range(k-1): bm.faces.new((T[i][j],T[i][j+1],T[i+1][j+1],T[i+1][j]))
        bm.faces.new((L[i],T[i][0],T[i+1][0],L[i+1])); bm.faces.new((T[i][-1],Rr[i],Rr[i+1],T[i+1][-1]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    top=[f for f in bm.faces if abs(f.normal.z)>0.5]
    if sum(f.normal.z for f in top)<0:
        bmesh.ops.reverse_faces(bm,faces=bm.faces)
    return link(name,bm,m)

BK=R+'montclair_state_pre_20261113ws112.blend'
for o in [o for o in bpy.data.objects if o.name.startswith('WS112_')]: bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections['WS112_CollegeAve_S_branch_walks']
TN=('Terrain_LiDAR_DTM_1m','WS110_ground_patch')
names=[]
with bpy.data.libraries.load(BK) as (src,dst):
    names=[n for n in src.objects if n.startswith(TN)]
    dst.objects=names
bk={}
for o in dst.objects:
    key=[t for t in TN if o.name.startswith(t)][0]; bk[key]=o
GB=[]
for t in TN:
    cur=O(t); b=bk[t]
    assert len(cur.data.vertices)==len(b.data.vertices)
    nres=0
    for vc,vb in zip(cur.data.vertices,b.data.vertices):
        if (vc.co-vb.co).length>1e-6: vc.co=vb.co.copy(); nres+=1
    cur.data.update(); print('E112 restored',t,nres)
    GB.append(bvh_of(b))
def zg(x,y):
    z=None
    for g in GB:
        h=g.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150)
        if h[0] is not None: z=h[0].z if z is None else max(z,h[0].z)
    return z
_dtm=dtm
def dtm(x,y):
    v=_dtm(x,y)
    return v if v is not None else zg(x,y)
nw=O('WS110_NormalAve_sidewalk'); mw=nw.data and nw.matrix_world
bmx=bmesh.new(); bmx.from_mesh(nw.data)
EDGEPTS=np.array([tuple(mw@v.co) for e in bmx.edges if e.is_boundary for v in e.verts if (mw@v.co).x< -263.5]); bmx.free()
if len(EDGEPTS): EDGEPTS[:,2]+=0.25
print('E112 edgepts',len(EDGEPTS))
NEW=[]
# ---------- 1. UNIFY #11: E walk N end -> brick link north to the Footpaths_OSM N walk (s -7)
ew=O('WS111_CollegeAve_S_E_walk'); co=np.array([tuple(ew.matrix_world@v.co) for v in ew.data.vertices])
s_,t_=st(co[:,0],co[:,1]); top=co[:,2]>np.percentile(co[:,2],5)
m0=(s_<s_.min()+0.05)
er=co[m0]; ers,ert=st(er[:,0],er[:,1]); S0=float(s_.min())
# top verts of end row: highest z per t
tin=float(ert.max()); tout=float(ert.min()); z_end=float(er[:,2].max())
print('E112 Ewalk end s %.2f t %.2f..%.2f z %.2f nverts %d'%(S0,tin,tout,z_end,len(er)))
SN=-7.0; TIN_N,TOUT_N=-6.7,-9.5
rows=[]
for s in list(np.arange(S0,SN,-0.5))+[SN]:
    u=min(max((S0-s)/(S0-(-1.5)),0),1); u=u*u*(3-2*u)
    a=tin*(1-u)+TIN_N*u; b=tout*(1-u)+TOUT_N*u
    r=[]
    for f in np.linspace(0,1,5):
        t=a+(b-a)*f; x,y=W(s,t); zd=dtm(x,y); z=(zd+0.04) if zd is not None else z_end
        wz=min(max((s-(S0-2.0))/2.0,0),1); wz=wz*wz*(3-2*wz)  # 1 at end row -> blend to walk end z
        z=z*(1-wz)+z_end*wz
        zf=zfp(x,y)
        if s<SN+1.5 and zf is not None: 
            v=min(max((SN+1.5-s)/1.5,0),1); z=z*(1-v)+(zf+0.012)*v
        r.append((x,y,z))
    rows.append(r)
o=ribbon(rows,'WS112_CollegeAve_S_E_walk_N_brick_link_to_Chapin_walk_ortho2020_UNIFY11_UNVERIFIED',M_brick); NEW.append(o)
print('E112 Elink rows',len(rows),'z',round(rows[0][0][2],2),round(rows[-1][0][2],2))
# ---------- 2. W branch walk y~-245 from College Ave W walk outer edge W to x -284 (2020 ortho)
wwk=O('WS111_CollegeAve_S_W_walk'); bw=bvh_of(wwk); w103=O('WS103_CollegeAve_S_W_sidewalk'); b103=bvh_of(w103)
def zw(x,y):
    for b in (bw,b103):
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150)
        if h[0] is not None: return h[0].z
    return None
P=np.array([(-254.6,-247.0),(-262.0,-245.6),(-270.0,-244.2),(-277.0,-243.2),(-284.0,-242.4)])
# densify with Catmull-like smoothing
pts=[]
for i in range(len(P)-1):
    for f in np.linspace(0,1,8,endpoint=False): pts.append(P[i]*(1-f)+P[i+1]*f)
pts.append(P[-1]); pts=np.array(pts)
k=np.ones(5)/5; sm=pts.copy()
for c in (0,1): sm[2:-2,c]=np.convolve(pts[:,c],k,'valid')
pts=sm; WID=2.6
# find E-end z: walk top at the W walk outer edge
zE=None
for dx in np.arange(0,2.0,0.1):
    zE=zw(pts[0][0]+dx,pts[0][1])
    if zE is not None: break
print('E112 Wbranch zE',zE)
rows=[]
for i,p in enumerate(pts):
    q=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]; q=q/np.linalg.norm(q); nn=np.array([-q[1],q[0]])
    dist=np.linalg.norm(p-pts[0])
    r=[]
    for f in np.linspace(-0.5,0.5,5):
        x,y=p+nn*WID*f; zd=dtm(x,y); z=zd+0.04 if zd is not None else (zE or 119)
        if zE is not None:
            v=min(max(1-dist/3.0,0),1); v=v*v*(3-2*v); z=z*(1-v)+(zE-0.006)*v
        r.append((float(x),float(y),float(z)))
    rows.append(r)
# extend first row 0.4 m east under the W walk to avoid a slot
q=pts[1]-pts[0]; q=q/np.linalg.norm(q)
r0=[(x-q[0]*0.4,y-q[1]*0.4,z) for x,y,z in rows[0]]; rows.insert(0,r0)
o=ribbon(rows,'WS112_W_branch_walk_y-245_to_Panzer_concrete_ortho2020_UNVERIFIEDwidth',M_conc); NEW.append(o)
print('E112 Wbranch rows',len(rows),'z',round(rows[1][2][2],2),round(rows[-1][2][2],2))
# ---------- 5. terrain: cap under new pieces, lift lawn to the Normal walk edge
bv=[bvh_of(o) for o in NEW]
from mathutils.kdtree import KDTree
kd=None
if len(EDGEPTS):
    kd=KDTree(len(EDGEPTS))
    for i,p in enumerate(EDGEPTS): kd.insert((p[0],p[1],0),i)
    kd.balance()
for tn in ('Terrain_LiDAR_DTM_1m','WS110_ground_patch'):
    to=O(tn); me=to.data; mw3=to.matrix_world; mi3=mw3.inverted(); ncap=0; nlift=0
    for v in me.vertices:
        p=mw3@v.co
        if not (-290<p.x<-230 and -275<p.y<-230): continue
        zmin=None
        for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
            for b in bv:
                h=b.ray_cast(Vector((p.x+dx,p.y+dy,150)),Vector((0,0,-1)),80)
                if h[0] is not None and h[0].z>p.z-2.0:
                    zz=h[0].z; zmin=zz if zmin is None else min(zmin,zz)
        if zmin is not None and p.z>zmin-0.05:
            p.z=zmin-0.05; v.co=mi3@p; ncap+=1; continue
        if kd is not None and p.x<-263:
            _,ii,dd=kd.find((p.x,p.y,0))
            if dd<1.2:
                ze=EDGEPTS[ii,2]-0.02
                if ze-0.35<p.z<ze:
                    w=1-dd/1.2; p.z=p.z+(ze-p.z)*w; v.co=mi3@p; nlift+=1
    me.update(); print('E112 cap',tn,ncap,'lift',nlift)

for o in bk.values(): bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_mainfile(); print('E112 SAVED')
