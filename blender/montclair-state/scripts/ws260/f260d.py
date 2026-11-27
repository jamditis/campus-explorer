# ws260d (CHAIN via ws208/merge208.py on ws260c): saw-cut joints on the WS115 College Ave S-leg E walk N part (OSM 312849086, x -236..-223,
# y -236..-202) = same build as ws259 f259b on WS103 (1.524 m, 1.5 cm dark strips 3 mm proud, draped on the walk's own top faces).
# Spacing UNVERIFIED. Aborts if the walk has modifiers (base-mesh drape would not match).
# The walk is mostly N-S: centreline from 0.5 m y-bins of its top-face verts (mid-x, smoothed), cuts perpendicular to it.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F260D'; SP=1.524; W2=0.0075; LIFT=0.003
TN='WS115_E_walk_N_concrete_OSM312849086_ortho2020_2m_UNVERIFIEDw'
TN=[n for n in bpy.data.objects.keys() if n.startswith(TN)][0]
SN='WS260_WS115_E_walk_N_sawcut_1p524m_UNVERIFIED'
if SN in bpy.data.objects: raise SystemExit('already in main')
o=bpy.data.objects[TN]
if len(o.modifiers): raise SystemExit('F260D walk has modifiers: '+str([m.name for m in o.modifiers]))
M=o.matrix_world
me=o.data; vs=[M@v.co for v in me.vertices]; ps=[]
for p in me.polygons:
    a,b,c=vs[p.vertices[0]],vs[p.vertices[1]],vs[p.vertices[2]]; cr=(b-a).cross(c-a)
    if cr.length>1e-9 and abs(cr.normalized().z)>0.96: ps.append(p.vertices[:])
bt=BVHTree.FromPolygons(vs,ps)
tv=np.array(sorted({i for p in ps for i in p})); xy=np.array([[vs[i].x,vs[i].y] for i in tv])
print(TAG,TN,'top faces',len(ps),'bbox %.2f %.2f %.2f %.2f'%(xy[:,0].min(),xy[:,0].max(),xy[:,1].min(),xy[:,1].max()),flush=True)
ys=np.arange(xy[:,1].min()+0.25,xy[:,1].max(),0.5); C=[];Wd=[]
for y in ys:
    s=xy[np.abs(xy[:,1]-y)<0.5]
    if len(s)<2: continue
    C.append(((s[:,0].min()+s[:,0].max())/2,y)); Wd.append(s[:,0].max()-s[:,0].min())
C=np.array(C); k=7; Cs=C.copy()
for i in range(len(C)): Cs[i,0]=C[max(0,i-k):i+k+1,0].mean()
seg=np.linalg.norm(np.diff(Cs,axis=0),axis=1); arc=np.concatenate([[0],np.cumsum(seg)])
print(TAG,'centreline pts',len(Cs),'length %.1f m'%arc[-1],'xwidth min/med/max %.2f %.2f %.2f'%(min(Wd),np.median(Wd),max(Wd)),flush=True)
def zhit(x,y):
    h=bt.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return h[0].z if h[0] else None
segs=[]
def line(p0,d,L,step=0.06):
    run=[]; prev=None
    for s in np.arange(0,L+1e-6,step):
        x,y=p0[0]+d[0]*s,p0[1]+d[1]*s; z=zhit(x,y)
        if z is not None and prev is not None and abs(z-prev)>0.025: z=None
        if z is None:
            if len(run)>=4: segs.append(run)
            run=[]; prev=None; continue
        run.append((x,y,z+LIFT)); prev=z
    if len(run)>=4: segs.append(run)
HW=max(Wd)/2+0.6
for a in np.arange(SP,arc[-1]-0.4,SP):
    i=min(np.searchsorted(arc,a),len(Cs)-1); i0=max(0,i-3); i1=min(len(Cs)-1,i+3)
    t=Cs[i1]-Cs[i0]; t=t/np.linalg.norm(t); n=np.array([-t[1],t[0]])
    f=(a-arc[i-1])/max(1e-6,arc[i]-arc[i-1]) if i>0 else 0; c=Cs[i-1]+(Cs[i]-Cs[i-1])*f if i>0 else Cs[0]
    line(c-n*HW,n,2*HW)
bm=bmesh.new()
for run in segs:
    P=[Vector(p) for p in run]; L=[];R=[]
    for i,p in enumerate(P):
        a=P[max(0,i-1)]; b=P[min(len(P)-1,i+1)]; d=(b-a); d.z=0; d.normalize(); nrm=Vector((-d.y,d.x,0))*W2
        L.append(bm.verts.new(p+nrm)); R.append(bm.verts.new(p-nrm))
    for i in range(len(P)-1): bm.faces.new((L[i],R[i],R[i+1],L[i+1]))
m2=bpy.data.meshes.new(SN); bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
bm.to_mesh(m2); bm.free()
mat=bpy.data.materials.get('MK_walk_sawcut_joint_dark'); m2.materials.append(mat)
ob=bpy.data.objects.new(SN,m2); o.users_collection[0].objects.link(ob)
lens=[np.hypot(r[-1][0]-r[0][0],r[-1][1]-r[0][1]) for r in segs]
print(TAG,'made',SN,'runs',len(segs),'run len min/med/max %.2f %.2f %.2f'%(min(lens),np.median(lens),max(lens)),'faces',len(m2.polygons),'mat',mat.name if mat else None,flush=True)
