import bpy, numpy as np
D='/workspace/nj-scenes/montclair-state/'
def load(f):
    with bpy.data.libraries.load(D+f) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
    o=b.objects[0]; P=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]); o.name='x'+f[-8:]; return P
A=load('montclair_state.blend'); B=load('montclair_state_ws206b.blend')
d=A[:,2]-B[:,2]; k=np.where(d>0.001)[0]
for i in k[np.argsort(-d[k])][:15]: print('C206 %.2f %.2f z %.3f -> %.3f (%.3f)'%(A[i,0],A[i,1],A[i,2],B[i,2],d[i]))
print('C206 n',len(k))
