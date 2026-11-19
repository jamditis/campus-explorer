# ws229 W53g: cumulative per-modifier ray heights at the residual SE samples (which modifier adds the +2.25 m at (205,-45))
import bpy,sys,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
P=[(145,-95),(150,-90),(155,-90),(165,-90),(165,-85),(165,-55),(180,-75),(185,-200),(185,-50),(190,-70),(195,-185),(195,-105),(195,-100),(205,-105),(205,-45),(215,-160),(220,-180),(225,-140),(225,-135),(235,-210),(235,-205)]
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
mods=[m for m in t.modifiers if m.show_render]
print('P229 mods',[(m.name,m.type, m.node_group.name if m.type=='NODES' and m.node_group else '') for m in mods],flush=True)
for m in t.modifiers: m.show_viewport=False
def ray():
    dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh()
    B=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
    out=[]
    for x,y in P:
        h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        out.append(None if h[0] is None else round(h[0].z-d(x,y),2))
    return out
R={'base':ray()}; print('P229 base',R['base'],flush=True)
for m in mods:
    m.show_viewport=True; R[m.name]=ray(); print('P229',m.name,R[m.name],flush=True)
json.dump({'pts':P,'R':R},open('/workspace/nj-scenes/montclair-state/scripts/ws229/probe229a.json','w'))
sys.stdout.flush(); import os; os._exit(0)
