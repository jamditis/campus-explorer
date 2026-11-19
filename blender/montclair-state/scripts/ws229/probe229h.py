# ws229 W53h: what fills the south scene-edge band (dz vs dtm_1m, whose index clamps to the y=-250 row south of the data)
# ws229 W53e: identify the flat grey sheet in the SE eye view from N (camera (238,-60,92.3) -> (240,-200,86.5)).
# Vertical rays at points ahead of the camera against every visible mesh whose bbox covers them (modifiers evaluated per object).
import bpy,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
PTS=[(x,y) for x in (150,180,210,240,246,252,262) for y in (-246,-249.5,-251,-254,-258,-265)]
cand=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    if min(b.x for b in bb)<262 and max(b.x for b in bb)>150 and min(b.y for b in bb)<-246 and max(b.y for b in bb)>-265: cand.append(o)
print('P229H cand',[o.name for o in cand],flush=True)
dg=bpy.context.evaluated_depsgraph_get()
for o in cand:
    for m in o.modifiers: m.show_viewport=m.show_render
dg.update()
hits={p:[] for p in PTS}
for o in cand:
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    if len(me.polygons)==0: e.to_mesh_clear(); continue
    B=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
    mats=[s.material.name if s.material else None for s in e.material_slots]
    for p in PTS:
        h=B.ray_cast(Vector((p[0],p[1],400)),Vector((0,0,-1)))
        if h[0] is not None:
            mi=me.polygons[h[2]].material_index; hits[p].append((round(h[0].z-d(*p),2),o.name,mats[mi] if mi<len(mats) else None))
    e.to_mesh_clear()
for p in PTS: print('P229H',p,sorted(hits[p],reverse=True)[:4],flush=True)
sys.stdout.flush(); import os; os._exit(0)
