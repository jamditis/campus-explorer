# ws255 WIPs/tests: W63f Feliciano E wall foot paving to the wall + base course re-cut (y 172..191)
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws255/extra255.json}
F=${F:-montclair_state_ws255a.blend}; TAGM=${TAGM:-ws255a}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws255}
[[ $ONLY == *1* ]] && srun "${CU1:--235,-140,120,230}" "${CAM1:--165.0,212.0,160.0,-193.0,181.0,137.5,30}" ${P}_oblique_W63f_Feliciano_E_wall_foot_and_base_course_from_NE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "${CU2:--215,-165,150,215}" "${CAM2:--190.6,196.0,140.6,-194.2,176.0,138.4,28}" ${P}_eye_W63f_Feliciano_E_wall_foot_paving_from_N_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "${CU3:--215,-165,150,215}" "${CAM3:--189.6,171.0,138.35,-194.0,188.0,139.3,28}" ${P}_eye_W63f_Feliciano_E_walk_and_wall_foot_from_S_stair_top_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "${CU4:--205,-180,165,195}" "${CAM4:--191.2,175.0,138.3,-194.6,180.0,138.0,24}" ${P}_closeup_W63f_base_course_recut_over_stairs_and_strip_${TAGM}_main_sub $F $D
true
