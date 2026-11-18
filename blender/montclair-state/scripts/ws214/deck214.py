import bpy, numpy as np
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if 'rhd' in n.lower() or 'red hawk' in n.lower() or 'redhawk' in n.lower()]
for o in b.objects:
    if o is None or o.type!='MESH' or not len(o.data.vertices): continue
    m=o.matrix_world; V=np.array([(m@v.co)[:] for v in o.data.vertices])
    sel=(V[:,0]>-282)&(V[:,0]<-258)&(V[:,1]>-46)&(V[:,1]<-34)
    if sel.sum()<3: continue
    W=V[sel]; zs=np.unique(np.round(W[:,2],1)); print('OBJ',o.name[:60],sel.sum(),'z',W[:,2].min().round(2),W[:,2].max().round(2),'levels',zs[:12])
