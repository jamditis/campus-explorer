import bpy, numpy as np
N=['WS35_CollegeAve_bed_posts_black_PHOTO_JOE_20261110','WS35_CollegeAve_bed_chain_black_PHOTO_JOE_20261110','T_PinOak_L1_0222','T_RedMaple_L1_0214','WS73_curb_back_lawn_verge_UNVERIFIED']
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (a,b): b.objects=N
for o in b.objects:
    mw=o.matrix_world; V=np.array([tuple(mw@v.co) for v in o.data.vertices])
    k=(V[:,1]>-116)&(V[:,0]<-203)
    print('DP',o.name[:30],len(V),k.sum(), V[k].min(0).round(2) if k.any() else '', V[k].max(0).round(2) if k.any() else '',flush=True)
    if 'Tree' in o.name or o.name.startswith('T_'):
        lo=V[V[:,2]<V[:,2].min()+1.0]; print('  trunkbase',lo.mean(0).round(2))
