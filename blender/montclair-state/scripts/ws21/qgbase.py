# ws21: QG north-strip patch deleted terrain faces whose centre hit the patch; where the patch has gaps this left 1-cell holes to the void (dark 'broken paving' cracks north of Life Hall).
# Instead keep the terrain under the patch, dropped 6 cm, as a backing skin.
import bpy,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
oe=o.evaluated_get(dg); me=oe.to_mesh(); M=o.matrix_world
print('EVAL faces',len(me.polygons))
T=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
def cnt(T):
    a=b=0
    for x in range(-60,120):
        for y in range(60,200):
            loc,n,i,d=T.ray_cast(Vector((x+.5,y+.5,200)),Vector((0,0,-1)))
            if loc is None:
                a+=1
                if -5<=x<60 and 95<=y<130: b+=1
    return a,b
print('MISS wide/court',cnt(T))
