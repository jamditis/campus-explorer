# ws262 WIPs: M2c police-lawn grass merge (f262b), W66 lawn skin E of the WS115 walk (f262a); main ws262c (also f262c Sprague make-local)
source scripts/ws262/srun262.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state_ws262c.blend}; TAGM=${TAGM:-ws262c}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws262}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json; EW=$PWD/scripts/ws262/extra262.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "${CU1:--400,-300,-80,40}" "${CAM1:--310.0,-40.0,145.0,-340.0,12.0,124.0,30}" ${P}_oblique_police_lawn_grass_merged_from_SE_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "${CU2:--400,-300,-80,40}" "${CAM2:--352.0,18.0,124.55,-336.0,14.0,125.0,28}" ${P}_eye_police_lawn_grass_from_W_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EW srun "${CU3:--240,-212,-232,-198}" "${CAM3:--219.5,-205.5,123.7,-226.5,-218.5,121.4,28}" ${P}_eye_lawn_E_of_WS115_W66_skin_from_N_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *4* ]] && EXTRAJ=$EP srun "${CU4:--400,-300,-80,40}" "${CAM4:--337.0,4.5,124.55,-339.0,9.5,124.05,32}" ${P}_closeup_police_lawn_grass_blades_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
