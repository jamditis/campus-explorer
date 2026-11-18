import bpy,numpy as np
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=['Terrain_LiDAR_DTM_1m']
o=[x for x in to.objects if x][0]
mw=o.matrix_world
V=np.array([tuple(mw@v.co) for v in o.data.vertices])
m=(V[:,0]>-252)&(V[:,0]<-170)&(V[:,1]>-150)&(V[:,1]<-55)
np.save('/workspace/nj-scenes/montclair-state/scripts/ws78/terrain_raw_box.npy',np.c_[np.nonzero(m)[0],V[m]])
print('WS78Q raw',m.sum(),flush=True)
sc=bpy.context.scene; sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh()
W=np.array([tuple(mw@v.co) for v in me.vertices]); m2=(W[:,0]>-252)&(W[:,0]<-170)&(W[:,1]>-150)&(W[:,1]<-55)
np.save('/workspace/nj-scenes/montclair-state/scripts/ws78/terrain_eval_box.npy',W[m2]); print('WS78Q eval',m2.sum(),len(W),len(V),flush=True)
