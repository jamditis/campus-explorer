# ws259 WIPs: Chapin W plaza after f258a (UNIFY #2 Footpaths residue retired)
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws259/extra259.json}
F=${F:-montclair_state_ws259a.blend}; TAGM=${TAGM:-ws259a}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws259}; CH=${CH:-ws257/crop257.py}
[[ $ONLY == *1* ]] && srun "${CU1:--262,-195,-232,-165}" "${CAM1:--252.0,-228.0,141.0,-218.0,-192.0,122.5,30}" ${P}_oblique_Chapin_W_plaza_and_stair_from_SW_high_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *2* ]] && srun "${CU2:--250,-195,-215,-175}" "${CAM2:--238.0,-206.0,123.4,-214.0,-194.0,123.0,28}" ${P}_eye_Chapin_W_plaza_from_CollegeAve_W_walk_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *3* ]] && srun "${CU3:--245,-195,-215,-160}" "${CAM3:--221.0,-178.0,125.6,-219.0,-200.0,122.6,28}" ${P}_eye_Chapin_W_plaza_from_N_connector_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *4* ]] && srun "${CU4:--240,-200,-215,-180}" "${CAM4:--226.5,-207.5,124.0,-219.0,-196.0,122.3,30}" ${P}_closeup_Chapin_W_plaza_old_OSM_junction_retired_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *5* ]] && srun "${CU5:--265,-215,-245,-180}" "${CAM5:--247.6,-233.0,121.55,-236.0,-200.0,121.4,28}" ${P}_eye_CollegeAve_S_W_walk_joints_from_S_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *6* ]] && srun "${CU6:--258,-228,-235,-205}" "${CAM6:--245.2,-225.5,121.35,-242.0,-215.0,120.5,32}" ${P}_closeup_CollegeAve_S_W_walk_sawcut_joints_${TAGM}_main_sub $F $D $CH
true
