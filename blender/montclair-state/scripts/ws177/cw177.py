import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS110_NormalAve_carriageway','WS110_NormalAve_curb'))]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
face=lambda t: -0.01462*t+0.292
for o in b.objects:
    M=np.array(o.matrix_world); V=np.array([v.co[:] for v in o.data.vertices]); W=V@M[:3,:3].T+M[:3,3]
    d=W[:,:2]-A; t=d@T; s=d@N; u=s-face(t); k=(t>80)&(t<110)&(u>-3)
    print(o.name[:30], sorted(set(np.round(u[k],2))), 'nt',len(set(np.round(t[k],1))))
