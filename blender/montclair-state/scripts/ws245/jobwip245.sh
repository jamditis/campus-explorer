# ws245 WIPs: main ws245a = ws244a + f245a (W62b pad-top margin + corner fans + graded east bank). Subset, terrain GN on.
source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws245/extra245.json
F=${F:-montclair_state_ws245a.blend}; TAGM=${TAGM:-ws245a}; D=${D:-wip}; ONLY=${ONLY:-1234}
[[ $ONLY == *1* ]] && srun "-420,-150,-60,220" "${CAM1:--385.0,-20.0,182.0,-268.0,100.0,134.0,30}" ws245_oblique_soccer_stands_pitch_M2c5_from_SW_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "-360,-200,20,180" "${CAM2:--326.0,96.0,135.3,-232.0,100.0,136.2,28}" ws245_eye_pitch_E_stands_from_W_sideline_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "-340,-200,10,180" "${CAM3:--300.0,31.0,135.5,-262.0,150.0,135.5,26}" ws245_eye_pitch_from_S_stand_walkway_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *4* ]] && srun "-290,-200,60,180" "${CAM4:--246.0,126.0,135.4,-226.0,132.0,134.4,30}" ws245_closeup_E_bank_graded_W62b_from_W_${TAGM}_main_sub $F $D ws239/upd239.py
true
