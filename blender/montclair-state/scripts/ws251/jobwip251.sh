# ws250 WIPs/tests: W63 ground N of the soccer field's east stand (lawn between Feliciano E face, Dickson N end, S of where University Hall stands in the north file)
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws251/extra251.json}
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws250c}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws250}
[[ $ONLY == *1* ]] && srun "${CU1:--240,-90,100,250}" "${CAM1:--112.0,118.0,182.0,-172.0,182.0,138.5,30}" ${P}_oblique_W63_lawn_N_of_Dickson_and_Feliciano_passage_from_SE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "${CU2:--215,-120,140,235}" "${CAM2:--146.0,192.0,140.8,-195.0,178.0,140.6,28}" ${P}_eye_W63_lawn_toward_Feliciano_from_E_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "${CU3:--215,-150,120,230}" "${CAM3:--186.0,205.0,140.8,-186.0,150.0,137.0,28}" ${P}_eye_Feliciano_Dickson_passage_from_N_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "${CU4:--200,-165,170,200}" "${CAM4:--178.5,180.5,140.2,-185.3,186.5,139.2,32}" ${P}_closeup_W63_tree_base_and_walk_edge_from_SE_${TAGM}_main_sub $F $D
true
