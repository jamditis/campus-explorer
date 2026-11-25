# ws238 four WIPs: main ws238a = ws237c + f237c (M3b seam tone feather, re-applied after the box restore lost ws237d). Subset, terrain + skirt GN on.
source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km} M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws235/extra235.json
F=${F:-montclair_state_ws238a.blend}; TAGM=${TAGM:-ws238a}; D=${D:-wip}; ONLY=${ONLY:-1234}
C="-480,-130,-150,540"
[[ $ONLY == *1* ]] && srun "$C" "-235.0,420.0,215.0,-360.0,200.0,117.0,26" ws238_oblique_rail_corridor_seam_tone_from_NE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "$C" "-338.0,140.0,122.6,-300.0,165.0,127.0,30" ws238_eye_PK_west_slope_tone_from_SW_rail_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "$C" "-370.0,-20.0,124.5,-320.0,0.0,121.5,30" ws238_eye_WS68_RHD_ground_seam_from_W_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "$C" "-310.0,215.0,125.4,-332.0,205.0,121.5,30" ws238_closeup_PK_M3b_seam_tone_${TAGM}_main_sub $F $D
true
