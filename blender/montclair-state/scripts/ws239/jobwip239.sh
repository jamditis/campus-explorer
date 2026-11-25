# ws239 four WIPs: main ws239b = ws238a + f239a (PK/M3b seam weld) + m2c239 (RHD SE entrance detail from north). Subset, terrain + skirt GN on.
source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km} M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws239/extra239.json
F=${F:-montclair_state_ws239b.blend}; TAGM=${TAGM:-ws239b}; D=${D:-wip}; ONLY=${ONLY:-1234}
C="-480,-130,-150,540"
[[ $ONLY == *1* ]] && srun "$C" "-200.0,-120.0,175.0,-285.0,-20.0,128.0,26" ws239_oblique_RHD_SE_Kasser_rail_corridor_from_SE_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *2* ]] && srun "$C" "-256.0,-62.0,126.6,-268.0,-42.0,127.4,30" ws239_eye_RHD_SE_entrance_from_College_Ave_S_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *3* ]] && srun "$C" "-338.0,140.0,122.6,-300.0,165.0,127.0,30" ws239_eye_PK_west_slope_seam_weld_from_SW_rail_${TAGM}_main_sub $F $D ws239/upd239.py
[[ $ONLY == *4* ]] && srun "$C" "-261.0,-51.5,126.3,-266.5,-42.0,127.6,35" ws239_closeup_RHD_SE_entrance_letters_lamp_door_${TAGM}_main_sub $F $D ws239/upd239.py
true
