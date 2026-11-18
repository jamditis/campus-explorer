import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n.startswith('UA_CollegeAve')]
out={}
for o in d.objects:
    if o.type!='MESH': continue
    me=o.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]; out[o.name[:60]]=W; print('DU',o.name,n,[m.type for m in o.modifiers])
np.savez('/workspace/nj-scenes/montclair-state/scripts/ws101/dumpua.npz',**out)
