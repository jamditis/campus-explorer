import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; return o
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; road=bpy.data.objects['Roads_OSM']
def hit(o,x,y):
    e=o.evaluated_get(dg); mi=o.matrix_world.inverted()
    ok,p,_,_=e.ray_cast(mi@Vector((x,y,200)),Vector((0,0,-1)))
    return (o.matrix_world@p).z if ok else None
for y in [v*1.0 for v in range(-56,-19)]:
    row=[]
    for x in (-5,-4,-3,-2,-1,0):
        r=hit(road,x,y); t=hit(ter,x,y)
        row.append('%+.2f'%(t-r) if (r and t) else ' none' if not r else ' r-only')
    print('y',y,' '.join(row), 'road@-3 %.2f'%(hit(road,-3,y) or 0))
