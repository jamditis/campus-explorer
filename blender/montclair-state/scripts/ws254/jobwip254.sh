# ws254 WIPs/tests: W63e Feliciano E recess stairs to the wall + entrance doors, flight A dip, walk N extension
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws254/extra254.json}
F=${F:-montclair_state_ws254a.blend}; TAGM=${TAGM:-ws254a}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws254}
[[ $ONLY == *1* ]] && srun "${CU1:--235,-140,120,230}" "${CAM1:--160.0,205.0,163.0,-190.0,172.0,136.0,30}" ${P}_oblique_W63e_Feliciano_E_recess_stairs_and_walk_N_end_from_NE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "${CU2:--215,-165,145,200}" "${CAM2:--186.5,158.0,135.75,-196.5,169.5,136.4,26}" ${P}_eye_W63e_Feliciano_E_recess_stairs_entrance_from_plaza_SE_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "${CU3:--210,-170,165,215}" "${CAM3:--189.9,195.5,140.45,-191.0,178.0,138.0,28}" ${P}_eye_W63e_walk_N_end_joined_to_OSM_walk_from_N_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "${CU4:--205,-180,155,180}" "${CAM4:--191.6,165.4,136.95,-197.5,167.6,136.4,24}" ${P}_closeup_W63e_entrance_doors_and_landing_to_wall_${TAGM}_main_sub $F $D
true
