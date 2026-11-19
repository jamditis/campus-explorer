# count stacked up-facing WS72 faces per grid point (overlaps), whole landing
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=L.matrix_world; me=L.data
V=[M@v.co for v in me.vertices]; T=BVHTree.FromPolygons(V,[p.vertices[:] for p in me.polygons])
xs=[v.x for v in V]; ys=[v.y for v in V]
import collections
pairs=collections.Counter(); n=0
y=min(ys)
while y<=max(ys):
    x=min(xs)
    while x<=max(xs):
        z=130; up=[]
        while True:
            h=T.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))
            if not h[0]: break
            if me.polygons[h[2]].normal.z>0.3: up.append(h[2])
            z=h[0].z-1e-4
        if len(up)>1: pairs[tuple(sorted(set(up)))]+=1; n+=1
        x+=0.05
    y+=0.05
print('P224 bbox x %.2f..%.2f y %.2f..%.2f'%(min(xs),max(xs),min(ys),max(ys)), 'stacked pts',n)
for k,c in pairs.most_common(30): print('P224 overlap',k,c)
