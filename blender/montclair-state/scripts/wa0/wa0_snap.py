"""wa0 snap: push WA0 fill boundary verts that face a Richardson wall onto the wall (+2 cm into it) to close the 0.1 m sawtooth at the wall foot."""
import bpy, math, json, os
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(names):
    V=[];P=[]
    for n in names:
        o=O[n]; e=o.evaluated_get(dg); m=e.to_mesh(); off=len(V)
        V+=[o.matrix_world@v.co for v in m.vertices]; P+=[tuple(off+i for i in p.vertices) for p in m.polygons]; e.to_mesh_clear()
    return BVHTree.FromPolygons(V,P)
BW=bvh(['QP_Richardson_ground_storey_glass_piers_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QQ_Richardson_entrance_doors_UNVERIFIED'])
BU=bvh(['WU_richardson_reid_LiDAR_patch_UNVERIFIED'])
F=O['WA0_richardson_wall_foot_fill_UNVERIFIED']; me=F.data
ec=defaultdict(int)
for p in me.polygons:
    L=list(p.vertices)
    for a,b in zip(L,L[1:]+L[:1]): ec[(min(a,b),max(a,b))]+=1
bv=set(i for e,c in ec.items() if c==1 for i in e)
moved=0; dmax=0
for i in bv:
    v=me.vertices[i]; x,y,z=v.co
    if BU.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] is not None: continue
    best=None
    for k in range(32):
        a=k*math.pi/16; d=Vector((math.cos(a),math.sin(a),0))
        h=BW.ray_cast(Vector((x,y,z+0.15)),d,0.16)
        if h[0] is None: continue
        if best is None or h[3]<best[0]: best=(h[3],d,h[1])
    if best and best[1].dot(best[2])<0:
        dist,d,n=best; v.co.x+=d.x*(dist+0.02); v.co.y+=d.y*(dist+0.02); moved+=1; dmax=max(dmax,dist)
me.update()
r=dict(boundary=len(bv),moved=moved,max_move_m=round(dmax,3)); print('SNAP',r,flush=True)
json.dump(r,open('/workspace/nj-scenes/montclair-state/data/wa0/snap_report.json','w'))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(compress=True); print('SAVED')
