import bpy, numpy as np
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b):
    b.objects=list(a.objects)
X0,X1,Y0,Y1=-272,-252,-60,-38
for o in b.objects:
    if not o or o.type!='MESH' or o.name.startswith(('Terrain','Context')): continue
    me=o.data; m=o.matrix_world
    if len(me.vertices)>400000: continue
    V=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',V); V=V.reshape(-1,3)
    if not len(V): continue
    M=np.array(m); V=V@M[:3,:3].T+M[:3,3]
    sel=(V[:,0]>X0)&(V[:,0]<X1)&(V[:,1]>Y0)&(V[:,1]<Y1)
    if sel.sum()<1: continue
    W=V[sel]; print('OBJ',o.name[:60],'|',len(V),sel.sum(),'x',W[:,0].min().round(1),W[:,0].max().round(1),'y',W[:,1].min().round(1),W[:,1].max().round(1),'z',W[:,2].min().round(2),W[:,2].max().round(2),[x.name[:25] for x in me.materials if x][:2])
