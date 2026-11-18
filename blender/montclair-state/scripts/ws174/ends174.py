import bpy, numpy as np
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith(('WS163_NormalAve','WS110_NormalAve','WS163_walk_back','WS110_CollegeAve')): continue
    V=np.array([(o.matrix_world@v.co)[:] for v in o.data.vertices]); d=V[:,:2]-A; s=d@N; t=d@T
    m=(t>-1.5)&(t<2.0)
    if not m.any(): continue
    print('OBJ',o.name,'mats',[mm.name for mm in o.data.materials])
    idx=np.where(m)[0]; idx=idx[np.argsort(s[idx])]
    for i in idx: print('   v%d s %.3f t %.3f z %.3f'%(i,s[i],t[i],V[i,2]))
