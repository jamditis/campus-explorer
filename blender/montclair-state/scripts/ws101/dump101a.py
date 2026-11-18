import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho',
'WS35_CollegeAve_bed_posts_black_PHOTO_JOE_20261110','WS35_CollegeAve_bed_chain_black_PHOTO_JOE_20261110',
'WS83_sprague_lane_walk_edge_band_concrete_UNVERIFIED','WS83_lane_gutter_skin_asphalt_UNVERIFIED','WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges',
'UA_CollegeAve_spur_1557427669_UNVERIFIED','WS86_grandstand_DTM_target','Terrain_LiDAR_DTM_1m','WS81_terrain_W_edge_curtain_lawn_UNVERIFIED_grade']
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n in names or n.startswith(('WS73_','WS40_','WS72b','WS92_'))]
out={}
for o in d.objects:
    if o.type!='MESH': continue
    me=o.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
    m=(W[:,0]>-262)&(W[:,0]<-185)&(W[:,1]>-175)&(W[:,1]<-100)
    print('D101',o.name[:60],n,int(m.sum()),[mm.type for mm in o.modifiers],me.users)
    if m.any(): out[o.name[:60]]=W[m]
np.savez('/workspace/nj-scenes/montclair-state/scripts/ws101/dump101_after.npz',**out)
