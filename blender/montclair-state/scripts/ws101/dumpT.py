import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): d.objects=['Terrain_LiDAR_DTM_1m']
o=d.objects[0]; me=o.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]; m=(W[:,0]>-230)&(W[:,0]<-120)&(W[:,1]>-200)&(W[:,1]<-100)
np.save('/workspace/nj-scenes/montclair-state/scripts/ws101/T_after101.npy',W[m]); print('DT ok')
