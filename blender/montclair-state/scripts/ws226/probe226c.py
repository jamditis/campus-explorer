import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
names=['QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch','QI_east_edge_delete_probe']
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
Bs={}
for n in names+['Terrain_LiDAR_DTM_1m']:
    o=bpy.data.objects[n]; M=o.matrix_world; me=o.data
    Bs[n]=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
def allz(B,x,y):
    z=400; hs=[]
    while len(hs)<4:
        h=B.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))
        if not h[0]: break
        hs.append(round(h[0].z,2)); z=h[0].z-0.02
    return hs
for x,y in [(140,100),(160,100),(200,100),(200,150),(200,190),(160,150),(230,50),(180,60),(215.7,66.9),(150,30),(196.9,-7.6),(173.9,-92.8)]:
    print('P226C',x,y,'dtm',round(float(A[int(y+250),int(x+250)]),2),{n[:4]:allz(B,x,y) for n,B in Bs.items()},flush=True)
# per-modifier evaluation at the same points
mods=list(t.modifiers)
for m in mods: m.show_viewport=False
for m in mods:
    if not m.show_render: continue
    m.show_viewport=True
    dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh()
    B=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
    print('P226C +%-34s'%m.name[:34],[allz(B,x,y)[:3] for x,y in [(200,150),(230,50),(180,60),(173.9,-92.8)]],flush=True)
sys.stdout.flush(); os._exit(0)
