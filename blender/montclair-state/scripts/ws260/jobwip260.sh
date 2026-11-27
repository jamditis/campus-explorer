# ws260 WIPs: UNIFY W64 bank W of the College Ave S-leg W walk (LiDAR ground patch joined into the terrain)
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws259/extra259.json}
F=${F:-montclair_state_ws260a.blend}; TAGM=${TAGM:-ws260a}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws260}; CH=${CH:-ws259/crop259.py}
[[ $ONLY == *1* ]] && srun "${CU1:--290,-215,-262,-185}" "${CAM1:--222.0,-258.0,141.0,-254.0,-222.0,119.5,28}" ${P}_oblique_W64_bank_W_of_CollegeAve_S_walk_from_SE_high_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *2* ]] && srun "${CU2:--272,-236,-248,-190}" "${CAM2:--250.6,-241.0,121.2,-257.0,-214.0,119.8,28}" ${P}_eye_W64_bank_from_S_walk_end_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *3* ]] && srun "${CU3:--272,-236,-248,-190}" "${CAM3:--256.5,-207.0,120.4,-249.0,-236.0,119.6,28}" ${P}_eye_W64_bank_from_N_lower_lawn_by_Panzer_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *4* ]] && srun "${CU4:--262,-238,-238,-215}" "${CAM4:--246.4,-232.0,121.6,-251.5,-225.5,119.9,30}" ${P}_closeup_W64_walk_edge_to_bank_${TAGM}_main_sub $F $D $CH
true
[[ $ONLY == *5* ]] && srun "${CU5:--245,-215,-240,-198}" "${CAM5:--234.6,-234.0,121.75,-228.0,-216.0,120.2,30}" ${P}_closeup_WS115_E_walk_sawcut_joints_from_S_${TAGM}_main_sub $F $D $CH
true
