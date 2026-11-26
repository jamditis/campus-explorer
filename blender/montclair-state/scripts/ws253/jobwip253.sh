# ws253 WIPs/tests: W63d Feliciano E walk + stairs, diagonal walk on the grass plot's NE side
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws253/extra253.json}
F=${F:-montclair_state_ws253c.blend}; TAGM=${TAGM:-ws253c}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws253}
[[ $ONLY == *1* ]] && srun "${CU1:--235,-140,120,230}" "${CAM1:--160.0,205.0,163.0,-187.0,169.0,136.0,30}" ${P}_oblique_W63d_Feliciano_E_stairs_and_diagonal_walk_from_NE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "${CU2:--215,-165,145,195}" "${CAM2:--180.5,173.5,138.45,-191.0,166.0,135.6,28}" ${P}_eye_W63d_Feliciano_E_stairs_from_diagonal_walk_E_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "${CU3:--215,-170,150,200}" "${CAM3:--191.3,160.3,135.75,-190.4,178.0,137.6,28}" ${P}_eye_W63d_Feliciano_E_walk_stairs_from_plaza_S_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "${CU4:--205,-178,152,178}" "${CAM4:--186.6,161.2,136.55,-190.6,165.2,134.7,30}" ${P}_closeup_W63d_stair_foot_cheek_and_raised_walk_end_${TAGM}_main_sub $F $D
true
