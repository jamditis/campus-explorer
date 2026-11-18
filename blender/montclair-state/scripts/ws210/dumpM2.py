import bpy, numpy as np
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
o=b.objects[0]; me=o.data; mw=o.matrix_world
om=me.attributes['bs_orig_mat'].data
R=[]
for p in me.polygons:
    q=mw@p.center
    if -224<q.x<-196 and -122<q.y<-88: R.append((q.x,q.y,q.z,p.material_index,om[p.index].value,p.normal.z))
np.save('/workspace/nj-scenes/montclair-state/scripts/ws210/TP.npy',np.array(R)); print('DM2',len(R),flush=True)
