source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws241/extra241.json
F=${F:-montclair_state_ws241b.blend}; TAGM=${TAGM:-ws241b}; D=${D:-test}; ONLY=${ONLY:-123}
CN="-230,60,850,1200"
[[ $ONLY == *1* ]] && srun "$CN" "${CAM1:--120.0,940.0,111.3,-80.0,1010.0,116.0,28}" ws241_eye_NJT_deck_S_face_W58_from_S_${TAGM} $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "$CN" "${CAM2:--152.0,922.0,112.8,-112.0,975.0,111.0,28}" ws241_eye_NJT_deck_SW_corner_notch_W58_from_SW_${TAGM} $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "-420,-300,-100,60" "${CAM3:--348.0,-64.0,120.3,-352.0,0.0,121.6,28}" ws241_eye_police_S_edge_W57_from_S_${TAGM} $F $D ws239/upd239.py
true
