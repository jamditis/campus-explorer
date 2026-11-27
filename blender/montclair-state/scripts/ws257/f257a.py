# ws257a (CHAIN via ws208/merge208.py on main ws256d): saw-cut contraction joints on the new Feliciano E paving (ws253-ws255):
# walk slabs, wall-foot paving to the wall, N extension to the OSM path, diagonal walk across the grass plot to Dickson NW.
# Evidence: the 2020 NJ ortho is too coarse (~0.3 m) to show joints here; the campus' other poured walks (ortho/Mapillary-era
# photos used for WS248 / MK / QT walks) use transverse saw-cuts at ~5 ft (1.524 m) -> same standard, UNVERIFIED for this walk.
# Geometry: one new object of thin dark strips (1.5 cm wide, 3 mm proud), sampled every 8 cm by downward ray casts against each
# target's own top faces (normal.z > 0.96 = slabs only, never stair treads/risers); runs break on misses or > 2.5 cm jumps.
# Transverse lines every 1.524 m perpendicular to each walk's axis + one longitudinal cold joint where the walk meets the
# wall-foot paving (x -192.0). Nothing north of y 188.2 (the OSM path crossing keeps its own surface). Main geometry untouched.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F257A'; SP=1.524; W2=0.0075; LIFT=0.003; YMAX=188.2
def tops(n):
    o=bpy.data.objects[n]; M=o.matrix_world; me=o.data; vs=[M@v.co for v in me.vertices]
    ps=[]
    for p in me.polygons:
        a,b,c=vs[p.vertices[0]],vs[p.vertices[1]],vs[p.vertices[2]]
        nz=abs((b-a).cross(c-a).normalized().z) if (b-a).cross(c-a).length>1e-9 else 0
        if nz>0.96: ps.append(p.vertices[:])
    return BVHTree.FromPolygons(vs,ps), np.array([[v.x,v.y] for v in vs])
def zhit(bt,x,y):
    h=bt.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
    return h[0].z if h[0] else None
SN='WS257_W63k_Feliciano_E_walk_sawcut_joints_1p524m_UNVERIFIED'
if SN in bpy.data.objects: raise SystemExit('already in main')
segs=[]   # list of point runs
PAD=(-184.25,-177.4,160.1,166.95)   # SE square pad of the diagonal walk (ws257a test plot): orthogonal grid there, not diagonal
def inpad(x,y): return PAD[0]<x<PAD[1] and PAD[2]<y<PAD[3]
def line(bt,p0,d,L,step=0.08,skip=None):
    run=[]; prev=None
    for s in np.arange(0,L+1e-6,step):
        x,y=p0[0]+d[0]*s,p0[1]+d[1]*s
        z=None if (y>YMAX or (skip and skip(x,y))) else zhit(bt,x,y)
        if z is not None and prev is not None and abs(z-prev)>0.025: z=None
        if z is None:
            if len(run)>=4: segs.append(run)
            run=[]; prev=None; continue
        run.append((x,y,z+LIFT)); prev=z
    if len(run)>=4: segs.append(run)
cnt={}
# (1) N-S walk pieces: transverse joints at y = Y0 + k*SP (shared y grid so the walk and wall-foot paving line up)
Y0=166.6
for n in ('WS253_W63d_Feliciano_E_walk_slabs','WS255_W63f_Feliciano_E_wall_foot_paving_to_wall_UNVERIFIED','WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED'):
    bt,xy=tops(n); k0=len(segs)
    x0,x1=xy[:,0].min()+0.02,xy[:,0].max()-0.02; y0,y1=xy[:,1].min(),xy[:,1].max()
    for k in range(0,40):
        y=Y0+k*SP
        if y<=y0+0.3 or y>=y1-0.3: continue
        line(bt,(x0,y),(1,0),x1-x0)
    cnt[n[:40]]=len(segs)-k0
# longitudinal cold joint at the walk / wall-foot paving seam (walk W edge x -192.0), on the paving side
bt,xy=tops('WS255_W63f_Feliciano_E_wall_foot_paving_to_wall_UNVERIFIED'); k0=len(segs)
line(bt,(-192.03,179.35),(0,1),YMAX-179.35); cnt['seam']=len(segs)-k0
# (2) diagonal walk: axis by PCA, transverse joints every SP along it
n='WS253_W63d_diagonal_walk_grass_plot_NE_to_Dickson_NW'; bt,xy=tops(n); k0=len(segs)
c=xy.mean(0); u,s,vt=np.linalg.svd(xy-c); ax=vt[0]; pr=vt[1]
t=(xy-c)@ax; w=(xy-c)@pr
print(TAG,'diag axis',ax.round(3),'len %.2f width %.2f'%(t.max()-t.min(),w.max()-w.min()),flush=True)
for tk in np.arange(t.min()+SP,t.max()-0.4,SP):
    p0=c+ax*tk+pr*(w.min()-0.5)
    line(bt,p0,pr,(w.max()-w.min())+1.0,0.06,skip=inpad)
cnt['diag']=len(segs)-k0; k0=len(segs)
# (2b) SE pad: square ~1.5 m panels aligned to its own x/y edges (pad corners from the test plot)
# pad's real edges from its own vertices; panels evenly divided (~SP each) so no sliver panel at the far edge
pv=xy[(xy[:,0]>PAD[0])&(xy[:,0]<PAD[1])&(xy[:,1]>PAD[2])&(xy[:,1]<PAD[3])]
ex0,ex1,ey0,ey1=pv[:,0].min(),pv[:,0].max(),pv[:,1].min(),pv[:,1].max(); nx=max(1,round((ex1-ex0)/SP)); ny=max(1,round((ey1-ey0)/SP))
print(TAG,'pad edges %.2f %.2f %.2f %.2f panels %dx%d (%.2f x %.2f m)'%(ex0,ex1,ey0,ey1,nx,ny,(ex1-ex0)/nx,(ey1-ey0)/ny),flush=True)
for i in range(1,nx): xk=ex0+i*(ex1-ex0)/nx; line(bt,(xk,PAD[2]+0.02),(0,1),PAD[3]-PAD[2]-0.04,0.06,skip=lambda x,y: not inpad(x,y))
for i in range(1,ny): yk=ey0+i*(ey1-ey0)/ny; line(bt,(PAD[0]+0.02,yk),(1,0),PAD[1]-PAD[0]-0.04,0.06,skip=lambda x,y: not inpad(x,y))
cnt['pad']=len(segs)-k0
# build strips
bm=bmesh.new()
for run in segs:
    P=[Vector(p) for p in run]
    L=[];R=[]
    for i,p in enumerate(P):
        a=P[max(0,i-1)]; b=P[min(len(P)-1,i+1)]; d=(b-a); d.z=0; d.normalize()
        nrm=Vector((-d.y,d.x,0))*W2
        L.append(bm.verts.new(p+nrm)); R.append(bm.verts.new(p-nrm))
    for i in range(len(P)-1): bm.faces.new((L[i],R[i],R[i+1],L[i+1]))
me=bpy.data.meshes.new(SN); bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
bm.to_mesh(me); bm.free()
mat=bpy.data.materials.get('MK_walk_sawcut_joint_dark')
me.materials.append(mat)
o=bpy.data.objects.new(SN,me)
bpy.data.objects['WS253_W63d_Feliciano_E_walk_slabs'].users_collection[0].objects.link(o)
print(TAG,'made',SN,'runs',len(segs),'verts',len(me.vertices),'faces',len(me.polygons),'per piece',cnt,'mat',mat.name if mat else None,flush=True)
