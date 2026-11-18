import bpy, numpy as np, os
from mathutils.bvhtree import BVHTree
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS110_','WS113_paving_tops_proxy'))]
sc=bpy.context.scene
for o in b.objects: sc.collection.objects.link(o)
if os.environ.get('FIX')=='1':
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177.py').read()); exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177b.py').read())
    if os.environ.get('FIXC')=='1': exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177c.py').read())
dg=bpy.context.evaluated_depsgraph_get()
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
pav=[o for o in b.objects if o.name.startswith(('WS110_NormalAve_carriageway','WS110_NormalAve_curb','WS110_NormalAve_sidewalk'))]
trees=[BVHTree.FromObject(o,dg) for o in pav]
for o in pav: print('MW',o.name[:30],[round(x,3) for x in o.matrix_world.translation])
g=next(o for o in b.objects if o.name.startswith('WS110_ground_patch'))
ge=g.evaluated_get(dg); me=ge.to_mesh(); M=g.matrix_world
W=np.array([(M@v.co)[:] for v in me.vertices])
d=W[:,:2]-A; t=d@T; s=d@N
res={}
for i in np.where((t>-5)&(t<200)&(s>-14)&(s<4))[0]:
    best=None
    for o,tr in zip(pav,trees):
        Mi=o.matrix_world.inverted(); pl=Mi@Vector((W[i,0],W[i,1],W[i,2]+50)); dl=(Mi.to_3x3()@Vector((0,0,-1))).normalized()
        h=tr.ray_cast(pl,dl,200)
        if h[0] is not None:
            z=(o.matrix_world@h[0]).z
            if best is None or z>best: best=z
    if best is not None:
        b_=int(t[i]//20)*20; res.setdefault(b_,[]).append(W[i,2]-best)
for k in sorted(res):
    a_=np.array(res[k]); print('BURY t %3d..%3d n %4d ground-paving max %+.2f  p90 %+.2f  n_above(>0.02) %d'%(k,k+20,len(a_),a_.max(),np.percentile(a_,90),(a_>0.02).sum()))
