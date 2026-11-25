# ws241 WIPs: main ws241h = ws240d + f241a-f (W58 NJT deck ground / notch fill, W57 WS68 edge + flap) + m2c241 (Ice Arena + Lot 28S/greenhouse) + f241g-i (ground under the new paving). Subset, terrain + skirt GN on.
source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws241/extra241.json
F=${F:-montclair_state_ws241h.blend}; TAGM=${TAGM:-ws241h}; D=${D:-wip}; ONLY=${ONLY:-1234}
CN="-230,60,850,1200"
[[ $ONLY == *1* ]] && srun "-300,20,540,780" "${CAM1:--262.0,528.0,168.0,-112.0,655.0,113.0,30}" ws241_oblique_Ice_Arena_Lot28S_from_SW_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "$CN" "${CAM2:--120.0,940.0,111.3,-80.0,1010.0,116.0,28}" ws241_eye_NJT_deck_S_face_ground_graded_W58_from_S_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "-420,-300,-100,60" "${CAM3:--348.0,-64.0,120.3,-352.0,0.0,121.6,28}" ws241_eye_police_S_edge_flap_W57_from_S_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *4* ]] && srun "${C4:--150,-50,580,660}" "${CAM4:--128.0,585.0,112.6,-108.0,611.0,112.6,32}" ws241_closeup_Ice_Arena_west_storefront_from_SW_${TAGM}_main_sub $F $D ws239/upd239.py
true
