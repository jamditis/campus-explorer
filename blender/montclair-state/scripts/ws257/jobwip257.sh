# ws257 WIPs: Feliciano E saw-cut joints (f257a) + Maintenance Building merge (f257b)
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws257/extra257.json}
F=${F:-montclair_state_ws257d.blend}; TAGM=${TAGM:-ws257d}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws257}; CH=${CH:-ws257/crop257.py}
[[ $ONLY == *1* ]] && EXTRAJ=$PWD/scripts/ws257/extra257u.json srun "${CU1:--305,-140,-345,-235}" "${CAM1:--150.0,-372.0,178.0,-228.0,-298.0,119.0,30}" ${P}_oblique_WS110_S_edge_feather_to_skirt_from_SE_high_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *2* ]] && srun "${CU2:--215,-165,150,215}" "${CAM2:--190.6,196.0,140.6,-194.2,176.0,138.4,28}" ${P}_eye_Feliciano_E_walk_joints_from_N_on_OSM_path_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *3* ]] && srun "${CU3:--215,-160,145,200}" "${CAM3:--178.3,160.8,138.5,-187.0,175.0,137.3,28}" ${P}_eye_diagonal_walk_joints_from_SE_pad_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *4* ]] && srun "${CU4:--215,-165,150,215}" "${CAM4:--189.4,187.0,140.5,-192.4,181.0,138.95,28}" ${P}_closeup_wall_foot_paving_and_walk_sawcut_joints_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *5* ]] && EXTRAJ=$PWD/scripts/ws257/extra257m.json srun "${CU5:--420,-280,-110,-10}" "${CAM5:--290.0,-118.0,160.0,-355.0,-58.0,121.0,30}" ${P}_oblique_Maintenance_Building_merged_from_SE_${TAGM}_main_sub $F $D $CH
true
