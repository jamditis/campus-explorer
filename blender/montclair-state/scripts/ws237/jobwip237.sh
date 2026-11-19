# ws237 four WIPs (skirt held under the ws236-lowered PK/WS60/WS68 edges), subset, terrain + skirt GN on
source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km} M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws235/extra235.json
F=${F:-montclair_state_ws237a.blend}; TAGM=${TAGM:-ws237a}; D=${D:-wip}; ONLY=${ONLY:-1234}
C="-480,-150,-130,540"
[[ $ONLY == *1* ]] && srun "$C" "-235.0,420.0,215.0,-360.0,200.0,117.0,26" ws237_oblique_PK_slope_skirt_held_under_from_NE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "$C" "-338.0,140.0,122.6,-300.0,165.0,127.0,30" ws237_eye_PK_west_slope_from_SW_rail_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "$C" "-306.0,332.0,118.4,-312.0,270.0,117.8,30" ws237_eye_PK_north_tip_from_N_trackside_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "$C" "-318.0,192.0,124.4,-302.0,197.0,125.0,35" ws237_closeup_PK_slope_former_skirt_blob_${TAGM}_main_sub $F $D
true
