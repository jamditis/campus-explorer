import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PRE=('WS163','WS110','WS172','WS173')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE) and 'skirt' not in n and 'CAM' not in n]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for o in b.objects:
    if o is None or o.type!='MESH': continue
    V=np.array([(o.matrix_world@v.co)[:] for v in o.data.vertices])
    if len(V)==0: continue
    d=V[:,:2]-A; s=d@N; t=d@T
    print('OBJ %-70s nv %6d s %7.2f..%7.2f t %7.2f..%7.2f z %6.2f..%6.2f mods %s'%(o.name,len(V),s.min(),s.max(),t.min(),t.max(),V[:,2].min(),V[:,2].max(),[m.type for m in o.modifiers]),flush=True)
