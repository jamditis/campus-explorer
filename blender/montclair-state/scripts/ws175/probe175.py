import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS110','WS174','WS163_NormalAve','WS163_walk','WS166','WS113_paving')) and 'CAM' not in n]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for o in b.objects:
    if o is None or o.type!='MESH': 
        if o: print('NONMESH',o.name,o.type); 
        continue
    mw=o.matrix_world; V=np.array([(mw@v.co)[:] for v in o.data.vertices]) if len(o.data.vertices) else np.zeros((0,3))
    if not len(V): continue
    d=V[:,:2]-A; s=d@N; t=d@T; sf=-0.01446*t-11.028; off=s-sf
    k=(t>0)&(t<186)&(off>-8)&(off<1.5)
    mods=[m.type+':'+m.name for m in o.modifiers]
    print('OBJ %-70s n %6d Sside %5d'%(o.name[:70],len(V),k.sum()), mods, o.hide_render, flush=True)
    if k.any():
        for a0 in (30,100):
            q=k&(t>a0)&(t<a0+6)
            if q.any(): print('   t%d off-bands'%a0, np.unique(np.round(off[q],2))[:30], 'z %.2f..%.2f'%(V[q,2].min(),V[q,2].max()))
