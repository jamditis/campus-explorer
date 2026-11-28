# ws268 probe B (merge208 CHAIN, NO SAVE): every mesh (scene or not) with vertices in the College Ave / Lot 33 box S of the police; z range, modifiers, visibility
import bpy, os, numpy as np
BX=(-392,-325,-48,-18)
sc=set(o.name for o in bpy.context.scene.objects)
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data or len(o.data.vertices)==0: continue
    n=len(o.data.vertices); co=np.empty(n*3,np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
    s=(W[:,0]>BX[0])&(W[:,0]<BX[1])&(W[:,1]>BX[2])&(W[:,1]<BX[3])
    if s.sum()==0: continue
    print('P268B',repr(o.name[:70]),'inscene',o.name in sc,'hr',o.hide_render,'nv',int(s.sum()),'z %.2f..%.2f'%(W[s,2].min(),W[s,2].max()),[(m.type,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers][:4],[ms.material.name for ms in o.material_slots if ms.material][:3],flush=True)
os._exit(0)
