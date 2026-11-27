# ws266 WIPs: police foundation/outbuilding bare band fill (f266a); main ws266a
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40} GATE=${GATE:-4300}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state_ws266a.blend}; TAGM=${TAGM:-ws266a}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws266}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "${CU1:--400,-300,-80,40}" "${CAM1:--385.0,-55.0,160.0,-338.0,10.0,124.0,30}" ${P}_oblique_police_lawn_overview_from_SW_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "${CU2:--400,-300,-80,40}" "${CAM2:--352.0,18.0,124.55,-336.0,14.0,125.0,28}" ${P}_eye_police_lawn_grass_from_W_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EP srun "${CU3:--400,-300,-80,40}" "${CAM3:--333.0,3.0,125.1,-341.0,-4.0,124.2,26}" ${P}_eye_police_east_face_foundation_edge_from_E_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && EXTRAJ=$EP srun "${CU4:--400,-300,-80,40}" "${CAM4:--337.0,7.5,124.4,-341.5,3.0,123.7,35}" ${P}_closeup_police_foundation_trimmed_grass_edge_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
