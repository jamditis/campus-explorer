# ws206 W26 (new, from the W25 close-up): the WS98 College Ave bend teardrop island (curb + mulch) was traced from LiDAR with a
# stair-stepped outline (0.2-0.5 m jogs on its W and SM sides, sawtooth visible at eye level). The NJ 2020 0.1 m ortho
# (scripts/ws206/ortho_isl.jpg, ov_isl.png) shows a clean light concrete curb: smooth arc on the NE (parallel to the College Ave
# bend), near-straight W side, smooth SM side and a rounded E tip. Rebuild: outer loop of the old curb resampled at 0.2 m,
# circular Gaussian-smoothed (sigma 1.0 m along the outline), pushed outward so it still encloses the old footprint (no
# uncovered slivers; max push printed), 0.15 m wide curb, top = adjacent paving + 0.15 m (paving sampled 0.25 m outside,
# smoothed along the loop), outer face dropped 6 cm under the paving; mulch = constrained Delaunay inside the inner loop, z from
# the old mulch where it existed (keeps the LiDAR mound) else curb top - 0.03. Old curb/mulch objects removed (no stacking).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
CU=ob('WS98_CollegeAve_bend_teardrop_island_CURB'); MU=ob('WS98_CollegeAve_bend_teardrop_island_MULCH')
TCU=bvh(CU); TMU=bvh(MU)
PAVN=['WS98_lotE_entry_aisle','WS76_accessible_lot_asphalt','WS27_CollegeAve_carriageway','WS205_lotE_entry_apron','WS75_sprague_lot_asphalt','WS79_lot_E_patch']
PT=[bvh(ob(n)) for n in PAVN]
def pavz(x,y):
    zs=[hz(t,x,y) for t in PT]; zs=[z for z in zs if z is not None]; return max(zs) if zs else None
# outer loop
bm=bmesh.new(); bm.from_mesh(CU.data); mw=CU.matrix_world
adj={}
for e in bm.edges:
    if e.is_boundary:
        a,b=e.verts[0].index,e.verts[1].index; adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
W={v.index:(mw@v.co) for v in bm.verts}; bm.free()
loops=[]; seen=set()
for s in adj:
    if s in seen: continue
    L=[s]; seen.add(s); prev=None; cur=s
    while True:
        nx=[n for n in adj[cur] if n!=prev and n not in seen]
        if not nx: break
        prev,cur=cur,nx[0]; L.append(cur); seen.add(cur)
    if len(L)>8: loops.append(L)
def area(P): x,y=P[:,0],P[:,1]; return 0.5*(x*np.roll(y,-1)-np.roll(x,-1)*y).sum()
LP=[np.array([(W[i].x,W[i].y) for i in L]) for L in loops]
O=max(LP,key=lambda P:abs(area(P)))
if area(O)<0: O=O[::-1]
print('F206b loops',len(LP),'outer pts',len(O),'area %.1f'%area(O),flush=True)
# resample 0.2 m
seg=np.sqrt(((np.roll(O,-1,0)-O)**2).sum(1)); s=np.r_[0,np.cumsum(seg)]; Ltot=s[-1]
OO=np.vstack([O,O[:1]]); st=np.arange(0,Ltot,0.2); R=np.c_[np.interp(st,s,OO[:,0]),np.interp(st,s,OO[:,1])]
n=len(R); sig=5.0; k=np.arange(-15,16); g=np.exp(-k**2/(2*sig**2)); g/=g.sum()
SM=np.zeros_like(R)
for i,kk in enumerate(k): SM+=g[i]*np.roll(R,-kk,0)
def normals(P):
    t=np.roll(P,-1,0)-np.roll(P,1,0); t/=np.linalg.norm(t,axis=1)[:,None]; return np.c_[t[:,1],-t[:,0]]  # outward for CCW
def inside(P,x,y):
    c=False; j=len(P)-1
    for i in range(len(P)):
        xi,yi=P[i]; xj,yj=P[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi: c=not c
        j=i
    return c
# outward push so SM encloses R: per-point push = max outside-distance of nearby R pts, smoothed
N=normals(SM); push=np.zeros(n)
for i,p in enumerate(R):
    if not inside(SM,p[0],p[1]):
        d=np.linalg.norm(SM-p,axis=1); j=int(d.argmin()); push[j]=max(push[j],d[j]+0.03)
pk=np.zeros(n); kk=np.arange(-12,13)
for i in range(n): pk[i]=max(push[(i+kk)%n]*np.clip(1-abs(kk)/12.5,0,1))
pk=np.convolve(np.r_[pk[-8:],pk,pk[:8]],np.ones(9)/9,'same')[8:-8]; pk=np.maximum(pk,0)
SM=SM+N*pk[:,None]
bad=sum(1 for p in R if not inside(SM,p[0],p[1]))
print('F206b smoothed outline pts',n,'max push %.2f'%pk.max(),'old outline pts still outside',bad,flush=True)
N=normals(SM); I=SM-N*0.15
# paving z
PZ=np.zeros(n)
for i,(p,q) in enumerate(zip(SM,N)):
    z=None
    for d in (0.25,0.4,0.6,0.9):
        z=pavz(p[0]+q[0]*d,p[1]+q[1]*d)
        if z is not None: break
    PZ[i]=z if z is not None else np.nan
ok=~np.isnan(PZ); PZ=np.interp(np.arange(n),np.arange(n)[ok],PZ[ok],period=n)
PZ=np.convolve(np.r_[PZ[-6:],PZ,PZ[:6]],np.ones(7)/7,'same')[6:-6]
TOP=PZ+0.15
print('F206b paving z %.2f..%.2f'%(PZ.min(),PZ.max()),flush=True)
# curb mesh
bm=bmesh.new()
vb=[bm.verts.new((SM[i,0],SM[i,1],PZ[i]-0.06)) for i in range(n)]
vo=[bm.verts.new((SM[i,0],SM[i,1],TOP[i])) for i in range(n)]
vi=[bm.verts.new((I[i,0],I[i,1],TOP[i])) for i in range(n)]
vd=[bm.verts.new((I[i,0],I[i,1],TOP[i]-0.12)) for i in range(n)]
for i in range(n):
    j=(i+1)%n
    bm.faces.new([vb[i],vb[j],vo[j],vo[i]]); bm.faces.new([vo[i],vo[j],vi[j],vi[i]]); bm.faces.new([vi[i],vi[j],vd[j],vd[i]])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('WS206_isl_curb'); bm.to_mesh(me); bm.free()
oc=bpy.data.objects.new('WS206_CollegeAve_bend_teardrop_island_CURB_smooth_ortho2020_UNVERIFIED',me)
CU.users_collection[0].objects.link(oc); me.materials.append(CU.data.materials[0] if CU.data.materials else None)
# mulch
pts=[tuple(p) for p in I]; m=len(pts)
x0,y0=I.min(0); x1,y1=I.max(0)
for x in np.arange(x0+0.15,x1,0.3):
    for y in np.arange(y0+0.15,y1,0.3):
        if inside(I,x,y) and np.min(np.linalg.norm(I-[x,y],axis=1))>0.12: pts.append((x,y))
res=delaunay_2d_cdt([Vector(p) for p in pts],[(i,(i+1)%m) for i in range(m)],[list(range(m))],1,1e-5)
V2,E2,F2=res[0],res[1],res[2]
def mz(x,y,ib):
    z=hz(TMU,x,y)
    dd=np.linalg.norm(I-[x,y],axis=1); j=int(dd.argmin()); zt=TOP[j]-0.03
    if z is None: return zt
    w=np.clip(dd[j]/0.6,0,1); return w*max(z,zt-0.05)+(1-w)*zt
bm=bmesh.new(); VV=[bm.verts.new((v.x,v.y,mz(v.x,v.y,None))) for v in V2]
for f in F2:
    try: bm.faces.new([VV[i] for i in f])
    except ValueError: pass
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
for it in range(6):  # relax mulch interior (keeps the mound, removes LiDAR dimples)
    nz={v:sum(e.other_vert(v).co.z for e in v.link_edges)/len(v.link_edges) for v in bm.verts if not v.is_boundary and v.link_edges}
    for v,z in nz.items(): v.co.z=0.5*v.co.z+0.5*z
me2=bpy.data.meshes.new('WS206_isl_mulch'); bm.to_mesh(me2); bm.free()
for p in me2.polygons: p.use_smooth=True
om=bpy.data.objects.new('WS206_CollegeAve_bend_teardrop_island_MULCH_smooth_ortho2020_UNVERIFIED',me2)
MU.users_collection[0].objects.link(om); me2.materials.append(MU.data.materials[0] if MU.data.materials else None)
print('F206b new curb faces',len(me.polygons),'mulch faces',len(me2.polygons),'top %.2f..%.2f'%(TOP.min(),TOP.max()),flush=True)
for o in (CU,MU): print('F206b removed',o.name,flush=True); bpy.data.objects.remove(o)
