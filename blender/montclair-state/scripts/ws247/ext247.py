import bpy, numpy as np, collections
F='/workspace/nj-scenes/montclair-state/montclair_state_ws247a.blend'
N=['fse_stand_under_pad','fs_turf','fse_stand_seating','fse_front_walkway','ft_fence_chainlink','fse_stand_understructure']
with bpy.data.libraries.load(F) as (a,b): b.objects=N
for o in b.objects:
    M=o.matrix_world; P=np.array([tuple(M@v.co) for v in o.data.vertices])
    print('E247',o.name,'x',P[:,0].min().round(1),P[:,0].max().round(1),'y',P[:,1].min().round(1),P[:,1].max().round(1),'z',P[:,2].min().round(2),P[:,2].max().round(2),flush=True)
    for y in (60,80,100,115):
        s=P[np.abs(P[:,1]-y)<2]
        if len(s): print('E247   y',y,'x',s[:,0].min().round(1),s[:,0].max().round(1),flush=True)
import os; os._exit(0)
