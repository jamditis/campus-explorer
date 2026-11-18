import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS16','WS17','WS15','WS14','WS13','WS12','WS11','WS10','WS8','WS9')) and 'skirt' not in n.lower()]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for o in b.objects:
    if o is None: continue
    if o.type=='MESH' and len(o.data.vertices):
        V=np.array([(o.matrix_world@v.co)[:] for v in o.data.vertices])
    else:
        V=np.array([o.matrix_world.translation[:]])
    d=V[:,:2]-A; s=d@N; t=d@T
    m=(s>-14.6)&(s<-9.5)&(t>-81)&(t<3)
    if m.any(): print('HIT %-75s %s n %d/%d s %.2f..%.2f t %.2f..%.2f'%(o.name,o.type,m.sum(),len(V),s[m].min(),s[m].max(),t[m].min(),t[m].max()),flush=True)
