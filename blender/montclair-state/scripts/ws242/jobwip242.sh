# ws242 WIPs: main ws242f = ws241h + f242a (skirt cracks) + f242b (W60 M3a flap) + f242c (M3b gap fill) + f242d-g (M3b edge flaps, normals, attrs, lawn slot) + m2c242/b (slice 4: 15 north objects). Subset, terrain + skirt GN on.
source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws242/extra242.json
F=${F:-montclair_state_ws242f.blend}; TAGM=${TAGM:-ws242f}; D=${D:-wip}; ONLY=${ONLY:-1234}
[[ $ONLY == *1* ]] && srun "-300,20,540,780" "${CAM1:--262.0,528.0,168.0,-112.0,655.0,113.0,30}" ws242_oblique_Lot28S_W_edge_flap_W60_from_SW_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "-420,-300,-100,60" "${CAM2:--348.0,-64.0,120.3,-352.0,0.0,121.6,28}" ws242_eye_police_S_edge_W59_from_S_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "${C3:--130,10,1010,1170}" "${CAM3:--38.0,1101.0,108.9,-62.0,1080.0,107.6,26}" ws242_eye_JR2_crossing_dropoff_loop_from_NE_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *4* ]] && srun "${C4:--420,-320,-90,0}" "${CAM4:--370.0,-62.0,120.2,-388.0,-34.0,118.6,30}" ws242_closeup_M3b_gap_fill_bank_W59_from_SE_${TAGM}_main_sub $F $D ws239/upd239.py
true
