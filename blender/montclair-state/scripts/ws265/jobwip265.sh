# ws265 WIPs: police flat lawn grass fill (f265a); main ws265a
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state_ws265a.blend}; TAGM=${TAGM:-ws265a}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws265}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json; EW=$PWD/scripts/ws263/extra263.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "${CU1:--400,-300,-80,40}" "${CAM1:--310.0,-40.0,145.0,-340.0,12.0,124.0,30}" ${P}_oblique_police_lawn_overview_from_SW_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "${CU2:--400,-300,-80,40}" "${CAM2:--352.0,18.0,124.55,-336.0,14.0,125.0,28}" ${P}_eye_police_lawn_grass_from_W_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EP srun "${CU3:--400,-300,-80,40}" "${CAM3:--337.0,-4.0,125.0,-342.0,20.0,124.3,28}" ${P}_eye_police_lawn_grass_fill_from_S_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && EXTRAJ=$EP srun "${CU4:--400,-300,-80,40}" "${CAM4:--343.5,6.5,124.1,-341.0,9.5,123.55,35}" ${P}_closeup_police_lawn_grass_fill_blades_soil_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
