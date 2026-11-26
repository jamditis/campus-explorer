# ws248 pass 1: W-side fill wedge under the back of the east stand, beside the ws247 back walk (W62e follow-up).
# The walk follows the LiDAR grade (133.3 -> 136.2 m S->N) but the stand pad / hold-under ground stays ~134.4,
# so the walk's W edge stood up to 1.28 m above the ground under the stand (raw 'wall' with no guard).
# Design: graded 1:2 fill from the walk edge down to the ground under the stand (seats are >= 3 m above: c248.out).
import bpy, os, sys, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
W='WS247_E_stand_back_walk_ortho2020_UNVERIFIED_level'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','fse_stand_under_pad',W]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T,PAD,WK=b.objects
for m in T.modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
box=(-245,-205,40,165)
def bvh(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    t=BVHTree.FromPolygons(vs,ps); e.to_mesh_clear(); return t
TB=bvh(T); PB=bvh(PAD)
def zg(x,y):
    zs=[]
    for t in (TB,PB):
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        if h[0] is not None: zs.append(h[0].z)
    return max(zs) if zs else None
V=np.array([v.co[:] for v in WK.data.vertices]).reshape(-1,6,3)
SL=float(os.environ.get('SL','2.0'))  # run per rise (1:2)
OFF=np.concatenate(([-0.03],np.arange(0.2,3.01,0.25)))  # first ring tucked 3 cm under the walk edge
rows=[];drops=[]
for r in V:
    w0=r[0]; d=w0[:2]-r[3][:2]; d/=np.linalg.norm(d); zt=w0[2]-0.03
    g=[zg(*(w0[:2]+d*o)) for o in OFF]; g=[gg if gg is not None else zt-1 for gg in g]
    drops.append(zt-g[0]); prof=[]
    for o,gg in zip(OFF,g):
        zs=zt-max(o,0)/SL
        prof.append((float(w0[0]+d[0]*o),float(w0[1]+d[1]*o),float(max(zs,gg-0.10))))
    rows.append(prof)
drops=np.array(drops); act=drops>0.15
# keep a 2-row ramp at each end of an active run so the wedge fades out
a2=act.copy()
for i in range(len(act)):
    if act[max(0,i-2):i+3].any(): a2[i]=True
Vv=[];Ff=[];idx={}
NP=len(OFF)
for i,pr in enumerate(rows):
    if not a2[i]: continue
    idx[i]=len(Vv); Vv+=pr
for i in range(len(rows)-1):
    if i in idx and i+1 in idx:
        a=idx[i]; b=idx[i+1]
        for k in range(NP-1): Ff.append((a+k,b+k,b+k+1,a+k+1))
print('H248 rows',len(rows),'active',int(act.sum()),'with ramps',int(a2.sum()),'max drop',round(float(drops.max()),2),'verts',len(Vv),'faces',len(Ff),flush=True)
ys=[rows[i][0][1] for i in range(len(rows)) if act[i]]; print('H248 active y',round(min(ys),1),round(max(ys),1),flush=True)
json.dump({'V':Vv,'F':Ff},open('/workspace/nj-scenes/montclair-state/scripts/ws248/h248.json','w'))
sys.stdout.flush(); os._exit(0)
