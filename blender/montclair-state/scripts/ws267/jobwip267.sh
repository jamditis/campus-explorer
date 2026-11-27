# ws267 WIPs: police south terrace-bed lawn (f267a) + pale deck-base strip grass (f267b); main ws267b
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40} GATE=${GATE:-4300}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state_ws267b.blend}; TAGM=${TAGM:-ws267b}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws267}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "${CU1:--400,-300,-80,40}" "${CAM1:--385.0,-55.0,160.0,-338.0,10.0,124.0,30}" ${P}_oblique_police_bed_and_deck_base_from_SW_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "${CU2:--400,-300,-80,40}" "${CAM2:--338.0,-3.0,125.0,-328.0,20.0,127.0,30}" ${P}_eye_deck_base_strip_grass_from_S_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EP srun "${CU3:--400,-300,-80,40}" "${CAM3:--333.0,3.0,125.1,-341.0,-4.0,124.2,26}" ${P}_eye_police_S_terrace_bed_from_NE_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && EXTRAJ=$EP srun "${CU4:--400,-300,-80,40}" "${CAM4:--343.0,-20.0,124.5,-347.0,-14.0,122.4,35}" ${P}_closeup_police_S_terrace_bed_lawn_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
