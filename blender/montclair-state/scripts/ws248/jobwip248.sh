# ws248 WIPs: main ws248e = ws247b + W62g (LiDAR ground E of the east stand, walk re-draped, joints). Subset, terrain GN on.
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws248/extra248.json
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws248e}; D=${D:-wip}; ONLY=${ONLY:-1234}
[[ $ONLY == *1* ]] && srun "-420,-150,-60,220" "${CAM1:--385.0,-20.0,182.0,-268.0,100.0,134.0,30}" ws248_oblique_soccer_field_E_side_LiDAR_ground_from_SW_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "-360,-200,20,180" "${CAM2:--326.0,96.0,135.3,-232.0,100.0,136.2,28}" ws248_eye_pitch_E_stand_from_W_sideline_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "-262,-186,40,160" "${CAM3:--199.0,128.0,136.0,-226.0,100.0,135.2,28}" ws248_eye_E_stand_back_walk_from_E_lawn_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *4* ]] && srun "-240,-200,80,140" "${CAM4:--221.6,94.0,136.1,-217.6,118.0,134.6,30}" ws248_closeup_back_walk_joints_W62g_from_S_on_walk_${TAGM}_main_sub $F $D "${CH4:-ws239/upd239.py}"
true
