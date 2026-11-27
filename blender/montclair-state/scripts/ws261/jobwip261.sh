# ws261 WIPs: UNIFY #32 crease feather on the lawn E of the WS115 walk + saw-cut joints on the WS129b Chapin S-drive N walk
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws261/extra261.json}
F=${F:-montclair_state_ws261d.blend}; TAGM=${TAGM:-ws261d}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws261}; CH=${CH:-ws259/crop259.py}
[[ $ONLY == *1* ]] && srun "${CU1:--252,-195,-265,-195}" "${CAM1:--196.0,-266.0,139.0,-222.0,-226.0,121.2,28}" ${P}_oblique_Chapin_S_drive_N_walk_and_lawn_E_of_WS115_from_SE_high_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *2* ]] && srun "${CU2:--245,-198,-252,-222}" "${CAM2:--204.5,-243.6,123.55,-226.0,-237.8,121.0,30}" ${P}_eye_Chapin_S_drive_N_walk_joints_from_E_end_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *3* ]] && srun "${CU3:--240,-212,-232,-198}" "${CAM3:--219.5,-205.5,123.7,-226.5,-218.5,121.4,28}" ${P}_eye_lawn_E_of_WS115_walk_crease_from_N_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *4* ]] && srun "${CU4:--236,-205,-250,-228}" "${CAM4:--212.5,-243.4,122.75,-221.5,-240.3,121.25,32}" ${P}_closeup_Chapin_S_drive_N_walk_sawcut_joints_${TAGM}_main_sub $F $D $CH
true
