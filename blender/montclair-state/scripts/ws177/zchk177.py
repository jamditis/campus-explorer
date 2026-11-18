import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS138b_ground_fill','WS134_ground_patch','WS110_','WS113_paving'))]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for o in b.objects:
    M=np.array(o.matrix_world); V=np.array([v.co[:] for v in o.data.vertices]); W=V@M[:3,:3].T+M[:3,3]
    d=W[:,:2]-A; t=d@T; s=d@N
    mods=[(m.type,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers]
    row=[]
    for tc in (80,100,120):
        for sc in (-8,-5,-2,0,2):
            k=(abs(t-tc)<1.5)&(abs(s-sc)<1.0)
            row.append('%d/%d:%s'%(tc,sc,('%.2f'%W[k,2].max()) if k.any() else '-'))
    print('Z',o.name[:40],mods,' '.join(row))
