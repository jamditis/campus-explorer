# W53 follow-up: the WQ_south_wood_tree_* woodland trees (NE wooded slope, x 140-200, y 145-212; no paving there) were
# placed on the old wrong upper terrain sheet; seat each trunk ring (local z~0) on the evaluated terrain - 0.05, both ways.
# (The NE corner has no 1 m LiDAR - dtm_1m is edge-padded there - but the terrain now matches the USGS 3DEP 10 m DEM.)
import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
DRY=os.environ.get('DRY','0')=='1'
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
sv=[m.show_viewport for m in t.modifiers]
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh(); M=t.matrix_world
B=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
for m,s in zip(t.modifiers,sv): m.show_viewport=s
n=0
for o in bpy.data.objects:
    if not o.name.startswith('WQ_south_wood_tree_') or o.type!='MESH' or o.parent is not None: continue
    Mw=o.matrix_world; ring=[v.co for v in o.data.vertices if abs(v.co.z)<0.03]
    if len(ring)<3: continue
    w=[Mw@q for q in ring]; x=sum(p.x for p in w)/len(w); y=sum(p.y for p in w)/len(w); z=min(p.z for p in w)
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is None: continue
    dz=(h[0].z-0.05)-z
    if abs(dz)>0.1:
        print('F226C',o.name,round(x,1),round(y,1),round(dz,2),flush=True); n+=1
        if not DRY: o.location.z+=dz
print('F226C seated',n,flush=True)
