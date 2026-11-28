# ws272 probe (no save): WS68 ground S-edge ridge (#4c). Modifiers on WS68, base verts in the band, evaluated z, neighbours.
import bpy, numpy as np, os
from mathutils import Vector
OB=bpy.data.objects
A=[o for o in OB if o.name.startswith('WS68_RHD_ground_northDTM')][0]
print('P272 A',A.name,'mw identity',A.matrix_world.is_identity if hasattr(A.matrix_world,'is_identity') else None,'verts',len(A.data.vertices),'hide_render',A.hide_render,flush=True)
for m in A.modifiers: print('P272 MOD',m.name,m.type,getattr(m,'node_group',None) and m.node_group.name,flush=True)
mw=A.matrix_world
V=np.array([tuple(mw@v.co) for v in A.data.vertices])
print('P272 bbox',V.min(0).round(1),V.max(0).round(1))
sel=(V[:,0]>-263)&(V[:,0]<-247)&(V[:,1]>-137)&(V[:,1]<-128)
S=V[sel]; print('P272 nband',len(S))
ys=np.unique(S[:,1].round(2)); xs=np.unique(S[:,0].round(2)); print('P272 ys',ys[:40]); print('P272 xs',xs[:40])
for y in sorted(ys,reverse=True):
    r=S[np.abs(S[:,1]-y)<0.01]; r=r[np.argsort(r[:,0])]
    print('P272 y',y,' '.join(f'{x:.1f}:{z:.2f}' for x,_,z in r[:24]),flush=True)
for o in OB:
    if o.type=='MESH' and any(s in o.name for s in ('WS60_terrain_edge_apron','WS86_grandstand_DTM_target')):
        print('P272 OBJ',o.name,'hide_render',o.hide_render,[m.name for m in o.modifiers])
for o in OB:
    for m in o.modifiers:
        if m.type=='NODES' and m.node_group and any(n.type=='OBJECT_INFO' and n.inputs['Object'].default_value==A for n in m.node_group.nodes):
            print('P272 USES_A',o.name,m.name)
os._exit(0)
