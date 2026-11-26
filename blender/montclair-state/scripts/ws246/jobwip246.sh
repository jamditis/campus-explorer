# ws246 WIPs: main ws246a = ws245a + f246a (east-bank lawn ortho-UV remap). Subset, terrain GN on (ws245 pattern).
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws246/extra246.json
F=${F:-montclair_state_ws246a.blend}; TAGM=${TAGM:-ws246a}; D=${D:-wip}; ONLY=${ONLY:-1234}
[[ $ONLY == *1* ]] && srun "-420,-150,-60,220" "${CAM1:--385.0,-20.0,182.0,-268.0,100.0,134.0,30}" ws246_oblique_soccer_field_E_bank_from_SW_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "-360,-200,20,180" "${CAM2:--326.0,96.0,135.3,-232.0,100.0,136.2,28}" ws246_eye_pitch_E_stand_and_bank_from_W_sideline_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "-262,-200,95,165" "${CAM3:--203.0,142.0,138.0,-226.0,118.0,135.5,26}" ws246_eye_E_stand_N_end_open_frame_from_NE_bank_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *4* ]] && srun "-262,-200,95,165" "${CAM4:--246.0,126.0,135.4,-226.0,132.0,134.4,30}" ws246_closeup_E_bank_lawn_tone_W62c_from_W_${TAGM}_main_sub $F $D "${CH4:-ws239/upd239.py}"
true
