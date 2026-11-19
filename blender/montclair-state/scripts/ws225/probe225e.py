# W53: which Terrain_LiDAR_DTM_1m modifier creates the upper sheet over the east side (3-14 m above dtm_1m.npy)?
import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; M=t.matrix_world
PTS=[(215.7,66.9),(184.5,185.0),(236.3,42.9),(239.7,-160.6),(127.1,68.9),(65.2,6.6),(174.4,244.7)]
print('P225E dtm',[round(float(A[int(y+250),int(x+250)]),2) for x,y in PTS],flush=True)
mods=list(t.modifiers); on=[m.show_render for m in mods]
for m in mods: m.show_viewport=False
def hits():
    dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh()
    B=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
    out=[]
    for x,y in PTS:
        z=300; hs=[]
        while len(hs)<4:
            h=B.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))
            if not h[0]: break
            hs.append(round(h[0].z,2)); z=h[0].z-0.01
        out.append(hs)
    return out
print('P225E base',hits(),flush=True)
for i,m in enumerate(mods):
    if not on[i]: continue
    m.show_viewport=True
    print('P225E +%-40s'%m.name[:40],m.type,hits(),flush=True)
sys.stdout.flush(); os._exit(0)
