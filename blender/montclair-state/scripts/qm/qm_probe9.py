import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for nm in ('PB_terrain_fan_regrid',):
    T.modifiers[nm].show_viewport=False; T.modifiers[nm].show_render=False
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
bt=BVHTree.FromObject(T,dg)
for y in (150,172):
    print('y',y,[ (x,round(bt.ray_cast(Vector((x+0.5,y+0.5,400)),Vector((0,0,-1)))[0].z,1)) for x in range(105,150,4)])
