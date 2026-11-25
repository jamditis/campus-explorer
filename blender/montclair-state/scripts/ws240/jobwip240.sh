# ws240 WIPs: main ws240c = ws239c + f240a (dark clearance bar) + m2c240 (police building, NJT deck + ramp, clock tower) + f240b/c (W12c lawn bank + ortho UV). Subset, terrain + skirt GN on.
source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km} M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws240/extra240.json
F=${F:-montclair_state_ws240c.blend}; TAGM=${TAGM:-ws240c}; D=${D:-wip}; ONLY=${ONLY:-1234}
CN="-230,60,850,1200"; CP="-480,-130,-150,540"
[[ $ONLY == *1* ]] && srun "$CN" "${CAM1:-40.0,890.0,185.0,-80.0,1025.0,112.0,28}" ws240_oblique_NJT_deck_ramp_clock_tower_from_SE_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "${C2:--420,-300,-60,60}" "${CAM2:--375.0,-5.0,120.5,-354.0,2.0,123.0,30}" ws240_eye_police_building_from_W_rail_corridor_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "$CN" "${CAM3:--120.0,940.0,111.3,-80.0,1010.0,116.0,28}" ws240_eye_NJT_deck_ramp_clock_tower_from_S_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *4* ]] && srun "${C4:--320,-220,-90,-10}" "${CAM4:--261.0,-51.5,126.3,-266.5,-42.0,127.6,35}" ws240_closeup_RHD_clearance_bar_dark_steel_${TAGM}_main_sub $F $D ws239/upd239.py
true
