# ws252 WIPs/tests: W63c Feliciano SE lower plaza, raised walk edge, E-W stairs up to Dickson's W walk, lamp
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws252/extra252.json}
F=${F:-montclair_state_ws252b.blend}; TAGM=${TAGM:-ws252b}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws252}
[[ $ONLY == *1* ]] && srun "${CU1:--240,-140,110,200}" "${CAM1:--228.0,118.0,160.0,-192.0,160.0,135.0,30}" ${P}_oblique_W63c_Feliciano_SE_plaza_stairs_from_SW_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "${CU2:--215,-165,140,180}" "${CAM2:--203.0,159.5,135.7,-184.0,157.3,136.8,28}" ${P}_eye_W63c_stairs_from_plaza_W_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "${CU3:--215,-165,135,180}" "${CAM3:--184.0,153.0,138.3,-200.0,161.0,135.0,28}" ${P}_eye_W63c_plaza_and_Feliciano_arcade_from_Dickson_W_walk_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "${CU4:--205,-178,148,172}" "${CAM4:--195.0,153.5,135.3,-189.8,157.5,134.7,30}" ${P}_closeup_W63c_stair_foot_and_raised_walk_edge_${TAGM}_main_sub $F $D
true
