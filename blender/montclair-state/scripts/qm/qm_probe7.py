import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
bt=BVHTree.FromObject(bpy.data.objects['Terrain_LiDAR_DTM_1m'],dg)
X=np.arange(0,220); Y=np.arange(20,262); Z=np.full((len(Y),len(X)),np.nan)
for j,y in enumerate(Y):
    for i,x in enumerate(X):
        h=bt.ray_cast(Vector((x+0.5,y+0.5,400)),Vector((0,0,-1)))[0]
        if h is not None: Z[j,i]=h.z
np.save('data/qm/terrain_scene_x0_y20.npy',Z); print('DONE')
