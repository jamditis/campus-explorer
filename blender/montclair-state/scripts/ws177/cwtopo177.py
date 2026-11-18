import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS110_NormalAve_carriageway',))]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
face=lambda t: -0.01462*t+0.292
o=b.objects[0]; me=o.data
V=np.array([v.co[:] for v in me.vertices]); d=V[:,:2]-A; t=d@T; s=d@N; u=s-face(t)
print('nv',len(V),'nf',len(me.polygons))
for p_ in me.polygons:
    vs=list(p_.vertices); tt=t[vs]
    if not (90<tt.mean()<100): continue
    print('F',p_.index,len(vs),'n_z %.2f'%p_.normal.z,' '.join('(t%.1f u%.2f z%.3f)'%(t[i],u[i],V[i,2]) for i in vs))
