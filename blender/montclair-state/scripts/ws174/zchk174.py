import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W=['WS163_NormalAve_W_S_curb_UNVERIFIEDsection','WS163_NormalAve_W_carriageway_LiDAR2023_int_edges_W11p3_UNVERIF','WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']
with bpy.data.libraries.load(p) as (a,b): b.objects=[n for n in a.objects if any(n.startswith(w) for w in W)]
P=np.vstack([np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/las163.npy'),np.load('/workspace/nj-scenes/montclair-state/prep/ws172_s77/las172.npy')]); P=P[P[:,3]==2]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
d=P[:,:2]-A; ls=d@N; lt=d@T; lz=P[:,2]
def L(s0,s1,t0):
    m=(ls>s0)&(ls<s1)&(abs(lt-t0)<1.0); return np.median(lz[m]) if m.sum()>3 else np.nan
for o in b.objects:
    V=np.array([(o.matrix_world@v.co)[:] for v in o.data.vertices]); dd=V[:,:2]-A; s=dd@N; t=dd@T
    print('OBJ',o.name)
    for tc in [-75,-65,-60,-47,-30,-20,-10,-3]:
        m=abs(t-tc)<0.3
        rows=sorted(set(np.round(s[m],2)))
        print('  t',tc,' '.join('s%.2f:z%.3f'%(r,V[m][np.round(s[m],2)==r][:,2].max()) for r in rows if r<-5),
              '| LiDAR gutter(-10.2..-9.9) %.3f  road(-9.6..-9.2) %.3f  walkfront(-10.7..-10.5) %.3f walkback(-12.1..-11.9) %.3f'%(L(-10.2,-9.9,tc),L(-9.6,-9.2,tc),L(-10.75,-10.5,tc),L(-12.1,-11.9,tc)))
