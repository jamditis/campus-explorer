import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
bt=BVHTree.FromObject(bpy.data.objects['Terrain_LiDAR_DTM_1m'],dg); bs=BVHTree.FromObject(bpy.data.objects['Context_skirt_3DEP_ortho_4km'],dg)
H=[]
for y in np.arange(-40.5,262,1.0):
    for x in np.arange(140.5,262,1.0):
        if bt.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is None and bs.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is None: H.append((x,y))
print('HOLES',len(H),H[:12])
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; print('SKMODS',[(m.name,m.type) for m in sk.modifiers])
