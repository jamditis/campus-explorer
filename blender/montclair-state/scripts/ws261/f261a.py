# ws261a (CHAIN via ws208/merge208.py on ws260d): saw-cut joints on the WS129b Chapin S-drive N walk (2.5 m concrete,
# x -234..-203.6, y -244..-236, mostly E-W) = same build as ws259 f259b / ws260 f260d (1.524 m = 5 ft, 1.5 cm dark strips
# 3 mm proud, draped on the walk's own top faces). Spacing UNVERIFIED. Generalised: centreline from 0.5 m bins along the
# walk's principal axis (PCA of top-face verts). Also a base-mesh clipping probe (print only): for a 0.25 m grid over the walk
# top, any other mesh face hit above walk top + 1 cm is reported (terrain/lawn poking through the walk).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F261A'; SP=1.524; W2=0.0075; LIFT=0.003
TN=[n for n in bpy.data.objects.keys() if n.startswith('WS129b_Chapin_S_drive_N_walk_concrete_2p5m')][0]
SN='WS261_WS129b_Chapin_S_drive_N_walk_sawcut_1p524m_UNVERIFIED'
if SN in bpy.data.objects: raise SystemExit('already in main')
o=bpy.data.objects[TN]
if len(o.modifiers): raise SystemExit('F261A walk has modifiers: '+str([m.name for m in o.modifiers]))
M=o.matrix_world; me=o.data; vs=[M@v.co for v in me.vertices]; ps=[]
for p in me.polygons:
    a,b,c=vs[p.vertices[0]],vs[p.vertices[1]],vs[p.vertices[2]]; cr=(b-a).cross(c-a)
    if cr.length>1e-9 and abs(cr.normalized().z)>0.96: ps.append(p.vertices[:])
bt=BVHTree.FromPolygons(vs,ps)
tv=np.array(sorted({i for p in ps for i in p})); xy=np.array([[vs[i].x,vs[i].y] for i in tv])
mu=xy.mean(0); U,S,Vt=np.linalg.svd(xy-mu,full_matrices=False); ax=Vt[0]; nx=np.array([-ax[1],ax[0]])
uv=np.stack([(xy-mu)@ax,(xy-mu)@nx],1)
print(TAG,TN,'top faces',len(ps),'axis %.3f %.3f'%tuple(ax),'u %.2f..%.2f'%(uv[:,0].min(),uv[:,0].max()),flush=True)
us=np.arange(uv[:,0].min()+0.25,uv[:,0].max(),0.5); C=[];Wd=[]
for u in us:
    s=uv[np.abs(uv[:,0]-u)<0.5]
    if len(s)<2: continue
    C.append((u,(s[:,1].min()+s[:,1].max())/2)); Wd.append(s[:,1].max()-s[:,1].min())
C=np.array(C); k=7; Cs=C.copy()
for i in range(len(C)): Cs[i,1]=C[max(0,i-k):i+k+1,1].mean()
Cs=np.array([mu+c[0]*ax+c[1]*nx for c in Cs])
seg=np.linalg.norm(np.diff(Cs,axis=0),axis=1); arc=np.concatenate([[0],np.cumsum(seg)])
print(TAG,'centreline pts',len(Cs),'length %.1f m'%arc[-1],'width min/med/max %.2f %.2f %.2f'%(min(Wd),np.median(Wd),max(Wd)),flush=True)
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
# --- clipping probe (base meshes) ---
X0,X1=xy[:,0].min(),xy[:,0].max(); Y0,Y1=xy[:,1].min(),xy[:,1].max()
SKIP=('T_','TREE','Roof_vent','Sky','Cloud','WS261_',TN,'Lamp','WS259_','WS260_')
objs=[]
for q in bpy.data.objects:
    if q.type!='MESH' or q.name.startswith(SKIP) or q.hide_render: continue
    mw=q.matrix_world; bb=[mw@Vector(c) for c in q.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    V=[mw@v.co for v in q.data.vertices]; P=[]
    for p in q.data.polygons:
        pv=[V[i] for i in p.vertices]
        if max(v.x for v in pv)<X0 or min(v.x for v in pv)>X1 or max(v.y for v in pv)<Y0 or min(v.y for v in pv)>Y1: continue
        P.append(tuple(p.vertices))
    if P: objs.append((q.name,BVHTree.FromPolygons(V,P)))
bad={}; n=0
for x in np.arange(X0,X1,0.25):
    for y in np.arange(Y0,Y1,0.25):
        z=zhit(x,y)
        if z is None: continue
        n+=1
        for nm,t in objs:
            h=t.ray_cast(Vector((x,y,z+2)),Vector((0,0,-1)),1.99)
            if h[0] is not None and h[0].z>z+0.01:
                d=bad.setdefault(nm,[0,0,None]); d[0]+=1; dz=h[0].z-z
                if dz>d[1]: d[1]=dz; d[2]=(round(x,2),round(y,2))
print(TAG,'probe samples',n,'objects',len(objs),flush=True)
for nm,d in sorted(bad.items(),key=lambda kv:-kv[1][0]): print(TAG,'ABOVE',nm[:70],'n',d[0],'max %.3f at'%d[1],d[2],flush=True)
print(TAG,'probe done',flush=True)
