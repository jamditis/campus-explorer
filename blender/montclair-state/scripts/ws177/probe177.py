import bpy, numpy as np, os
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PRE=('WS110_NormalAve','WS163_NormalAve_W','WS174_junction_bridge','WS113_paving_tops_proxy','WS110_ground_patch')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE)]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
out=[]
for o in b.objects:
    if o is None or o.type!='MESH': continue
    M=np.array(o.matrix_world); V=np.array([v.co[:] for v in o.data.vertices]);
    if len(V)==0: continue
    W=V@M[:3,:3].T+M[:3,3]; d=W[:,:2]-A; t=d@T; s=d@N
    k=(t>-8)&(t<12)
    print('OBJ',o.name,len(V),k.sum(),flush=True)
    for i in np.where(k)[0]: out.append((o.name,int(i),float(t[i]),float(s[i]),float(W[i,2])))
import json; json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws177/probe177.json','w'))
print('DONE',len(out))
