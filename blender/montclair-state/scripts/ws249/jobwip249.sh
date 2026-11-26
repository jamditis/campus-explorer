# ws249 WIPs/tests: main ws249e = ws248g + W slope LiDAR snap on PK fill (f249a) + SE berm snap/patch (f249a-d) + M3b snap (f249e). Subset, terrain GN on.
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt PK_Feliciano_west_DTM_fill_UNVERIFIED" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws249/extra249.json}
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws249e}; D=${D:-wip}; ONLY=${ONLY:-1234}; P=${P:-ws249}
[[ $ONLY == *1* ]] && srun "${CU1:--420,-150,-60,220}" "${CAM1:--395.0,40.0,175.0,-262.0,110.0,128.0,30}" ${P}_oblique_soccer_field_W_slope_and_SE_berm_from_W_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "${CU2:--360,-250,100,210}" "${CAM2:--336.0,150.0,122.8,-300.0,150.0,132.5,28}" ${P}_eye_W_embankment_up_to_pitch_from_W_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "${CU3:--225,-160,30,100}" "${CAM3:--176.0,72.0,137.2,-197.0,54.0,137.6,28}" ${P}_eye_E_stand_SE_berm_from_NE_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *4* ]] && srun "${CU4:--330,-280,130,185}" "${CAM4:--313.0,147.0,129.6,-300.0,160.0,133.0,30}" ${P}_closeup_W_slope_top_turf_edge_light_pole_from_SW_${TAGM}_main_sub $F $D ws239/upd239.py
true
