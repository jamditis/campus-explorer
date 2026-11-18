import bpy, numpy as np
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(M) as (s,d): d.objects=['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']
o=d.objects[0]; me=o.data; co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); mw=np.array(o.matrix_world); W=co@mw[:3,:3].T+mw[:3,3]
np.save('/tmp/ws110patch.npy',W); print('BB',W.min(0),W.max(0),len(W))
