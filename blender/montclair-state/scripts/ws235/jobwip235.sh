# ws235 four WIPs (M3b west rail corridor: north 1 m LiDAR DTM under the Montclair Line y -116..515), subset, terrain + skirt GN on
source scripts/ws226/srun226.sh
# Codex #44: cutrend189 hides every Context_skirt object unless HIDE is set, so the seam views must override it to show the skirt
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km}" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws235/extra235.json
F=${F:-montclair_state_ws235b.blend}; TAGM=${TAGM:-ws235b}; D=${D:-wip}; ONLY=${ONLY:-1234}
true
export KEEPMOD="$KEEPMOD M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam"
C="-480,-150,-130,540"
[[ $ONLY == *1* ]] && srun "$C" "-235.0,420.0,215.0,-360.0,200.0,117.0,26" ws235_oblique_west_rail_corridor_M3b_from_SE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "$C" "-350.0,172.0,120.0,-322.0,262.0,118.2,30" ws235_eye_Montclair_Line_corridor_M3b_from_S_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "$C" "-251.0,442.0,117.6,-300.0,342.0,116.4,30" ws235_eye_Montclair_Line_corridor_M3b_from_N_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "$C" "-331.0,234.0,119.3,-338.5,250.0,117.6,30" ws235_closeup_Montclair_Line_ballast_on_M3b_${TAGM}_main_sub $F $D
true
