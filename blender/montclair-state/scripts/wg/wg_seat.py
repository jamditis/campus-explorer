import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
d=O['QY_walk_junction_wear_decals_UNVERIFIED']; me=d.data; mw=d.matrix_world; mwi=mw.inverted()
P=np.array([mw@v.co for v in me.vertices]); lo=P.min(0)-1; hi=P.max(0)+1
WM=('QT_walk','OV_Paving','gk_walk','OY_walk_panel','PA_walk')
B=[]
for o in O:
    if o.type!='MESH' or o==d or o.hide_render or 'soil_edge' in o.name: continue
    if not any(s.material and s.material.name.startswith(WM) for s in o.material_slots): continue
    bb=np.array([o.matrix_world@Vector(c) for c in o.bound_box])
    if (bb.max(0)[:2]<lo[:2]).any() or (bb.min(0)[:2]>hi[:2]).any(): continue
    e=o.evaluated_get(dg); m=e.to_mesh()
    B.append((o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]))); e.to_mesh_clear()
print('walk objs',len(B))
W=np.array([x.value for x in me.attributes['qy_w'].data]); N=len(W)
nb=[[] for _ in range(N)]
for e in me.edges: a,b=e.vertices; nb[a].append(b); nb[b].append(a)
mask=np.zeros(N); dz=[]
for i,v in enumerate(me.vertices):
    p=mw@v.co; zs=[]
    for n,b in B:
        h=b.ray_cast(Vector((p.x,p.y,p.z+0.15)),Vector((0,0,-1)),0.30)
        if h[0] is not None: zs.append(h[0].z)
    if zs:
        nz=max(zs)+0.006; dz.append(nz-p.z); p.z=nz; v.co=mwi@p; mask[i]=1
dz=np.array(dz); print('seated',len(dz),'off',int(N-mask.sum()),'dz p5/p50/p95/max',*np.round(np.percentile(dz,[5,50,95,100]),4))
# off-walk verts: flatten to neighbouring seated height so edge faces don't dip into the slab
Z=np.array([(mw@v.co).z for v in me.vertices]); done=mask.copy()
for it in range(6):
    nd=done.copy()
    for i in range(N):
        if done[i]: continue
        s_=[Z[j] for j in nb[i] if done[j]]
        if s_: Z[i]=max(s_); nd[i]=1
    done=nd
for i,v in enumerate(me.vertices):
    if not mask[i]:
        p=mw@v.co; p.z=Z[i]; v.co=mwi@p
print('flattened off-walk',int(done.sum()-mask.sum()))
# off-walk verts: (z flattened); smooth weights to remove sawtooth, then clamp to on-walk
for it in range(int(os.environ.get('SMOOTH','5'))):
    W=np.array([0.5*W[i]+0.5*np.mean(W[nb[i]]) if nb[i] else W[i] for i in range(N)])
W=W*mask
for i,x in enumerate(me.attributes['qy_w'].data): x.value=float(W[i])
print('qy_w final p50/p90/max',*np.round(np.percentile(W,[50,90,100]),3))
me.update()
