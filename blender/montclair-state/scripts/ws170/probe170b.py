import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W=['WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED','WS163_NormalAve_W_S_curb_UNVERIFIEDsection','WS163_walk_back_lawn_lip_S_UNVERIFIED','WS110_NormalAve_sidewalk_ws85prep_ortho2020_UNVERIFIED','WS110_NormalAve_curb_W11p3_ws84prep_ortho2020_UNVERIFIED','WS163_NormalAve_W_carriageway_LiDAR2023_int_edges_W11p3_UNVERIF']
with bpy.data.libraries.load(p) as (a,b): b.objects=[n for n in a.objects if n in W]
for o in b.objects:
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    for px,py in ((-349.5,-255.55),(-317.5,-263.55),(-271.0,-275.18)):
        n=[v for v in vs if abs(v.x-px)<1.2 and abs(v.y-py)<6]
        if n: print('S',o.name[:40],px,'y %.2f..%.2f z %.2f..%.2f'%(min(v.y for v in n),max(v.y for v in n),min(v.z for v in n),max(v.z for v in n)),flush=True)
