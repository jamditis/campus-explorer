import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    names=[n for n in a.objects]
    b.objects=[n for n in names if n.startswith(('WS1','WS9','WS8','UA_','PZ','LOT'))]
print('NAMES',len(names),'LOADED',len(b.objects),flush=True)
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for o in b.objects:
    if o is None or o.type!='MESH' or len(o.data.vertices)==0: continue
    M=np.array(o.matrix_world); V=np.array([v.co[:] for v in o.data.vertices]); W=V@M[:3,:3].T+M[:3,3]
    d=W[:,:2]-A; t=d@T; s=d@N; k=(t>55)&(t<185)&(s>-3)&(s<6)&(W[:,2]>110)
    if k.sum()>0: print('BANDN',o.name[:70],'hide_render',o.hide_render,'n',k.sum(),'z %.2f..%.2f'%(W[k,2].min(),W[k,2].max()),flush=True)
