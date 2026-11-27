# ws264 WIPs: M5 cleanup (paths relative, 110 empty stubs removed; NaN proxy kept, grade output unchanged); main ws264c
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state_ws264c.blend}; TAGM=${TAGM:-ws264c}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws264}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json; EW=$PWD/scripts/ws263/extra263.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "${CU1:--400,-300,-80,40}" "${CAM1:--310.0,-40.0,145.0,-340.0,12.0,124.0,30}" ${P}_oblique_police_lawn_overview_from_SW_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "${CU2:--400,-300,-80,40}" "${CAM2:--352.0,18.0,124.55,-336.0,14.0,125.0,28}" ${P}_eye_police_lawn_grass_from_W_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EW srun "${CU3:--240,-212,-232,-198}" "${CAM3:--219.5,-205.5,123.7,-226.5,-218.5,121.4,28}" ${P}_eye_lawn_E_of_WS115_W66_whole_strip_skin_from_N_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *4* ]] && EXTRAJ=$EW srun "${CU4:--232,-200,-216,-192}" "${CAM4:--209.5,-208.5,124.6,-216.0,-202.0,122.9,30}" ${P}_closeup_Chapin_W_plaza_edge_WS113_grade_unchanged_${TAGM}_main_sub $F $D $CH
true
