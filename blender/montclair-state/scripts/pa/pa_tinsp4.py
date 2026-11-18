import bpy, numpy as np
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
co=np.zeros(len(me.vertices)*3,dtype=np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
np.save('/workspace/nj-scenes/montclair-state/data/pa/terrain_verts.npy',co)
print('TI saved',co.shape)
