# ws248 probe: walk W edge vs ground/pad just W of it (under the east stand), from the evaluated terrain
import bpy, os, sys, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
W='WS247_E_stand_back_walk_ortho2020_UNVERIFIED_level'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','fse_stand_under_pad',W]
names=[o.name for o in b.objects if o]; print('P248 objs',len(names),[n for n in names if n.startswith('fse')][:40],flush=True)
for o in b.objects:
    if o: bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
box=(-245,-205,40,165)
def bvh(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    t=BVHTree.FromPolygons(vs,ps) if ps else None; e.to_mesh_clear(); return t,len(ps)
T,nt=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m']); P,np_=bvh(bpy.data.objects['fse_stand_under_pad'])
Wo=bpy.data.objects[W]; me=Wo.data; V=np.array([v.co[:] for v in me.vertices]).reshape(-1,6,3)
print('P248 terrain faces',nt,'pad faces',np_,'rows',len(V),flush=True)
def zr(t,x,y):
    if t is None: return None
    h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return None if h[0] is None else round(h[0].z,2)
out=[]
for i in range(0,len(V),6):
    r=V[i]; w0=r[0]; e0=r[3]; d=w0[:2]-e0[:2]; d/=np.linalg.norm(d)
    s=[]
    for off in (0.1,0.5,1.0,2.0,4.0):
        p=w0[:2]+d*off; s.append((zr(T,*p),zr(P,*p)))
    print('P248 y %.1f xw %.2f walk %.2f skirtW %.2f | T/pad at +0.1 %s +0.5 %s +1 %s +2 %s +4 %s'%(w0[1],w0[0],w0[2],r[4][2],*s),flush=True)
sys.stdout.flush(); os._exit(0)
