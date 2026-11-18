import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W=['WS110_NormalAve_curb_W11p3_ws84prep_ortho2020_UNVERIFIED','WS110_NormalAve_carriageway_W11p3_ws84prep_ortho2020_UNVERIFIED','WS110_NormalAve_sidewalk_ws85prep_ortho2020_UNVERIFIED','WS163_NormalAve_W_S_curb_UNVERIFIEDsection','WS163_NormalAve_W_carriageway_LiDAR2023_int_edges_W11p3_UNVERIF','WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if any(n.startswith(w) for w in W)]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for o in b.objects:
    V=np.array([(o.matrix_world@v.co)[:] for v in o.data.vertices]); d=V[:,:2]-A; s=d@N; t=d@T
    print('OBJ',o.name,flush=True)
    for tc in [-78,-60,-40,-20,-5,-1.5,-0.82,0,1.3,3,5,8,10,15,20,25,30]:
        m=(abs(t-tc)<0.6)&(s<-5)
        if m.sum(): print('   t %6.2f  S-side s %s'%(tc,np.round(np.unique(np.round(s[m],2)),2)[:12]),flush=True)
