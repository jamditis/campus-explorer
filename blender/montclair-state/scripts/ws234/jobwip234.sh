# ws234 four WIPs (M2b station/rail batch + M3a north LiDAR terrain extension), subset, terrain GN on, skirt GN on (KEEPMOD)
source scripts/ws226/srun226.sh
# Codex #44: cutrend189 hides every Context_skirt object unless HIDE is set, so the seam views must override it to show the skirt
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km}" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws234/extra234.json
F=${F:-montclair_state_ws234e.blend}; TAGM=${TAGM:-ws234e}; D=${D:-wip}; ONLY=${ONLY:-1234}
[[ $ONLY == *1* ]] && srun "-250,60,600,1250" "45.0,950.0,145.0,-25.0,1090.0,108.0,32" ws234_oblique_MSU_station_M2b_M3a_from_SE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "-250,60,600,1250" "-30.0,1040.0,111.5,-12.0,1150.0,110.5,30" ws234_eye_MSU_station_platform_from_S_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "-250,60,600,1250" "-100.0,690.0,112.6,-150.0,790.0,111.5,30" ws234_eye_Childrens_Center_from_SE_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "-250,60,600,1250" "-94.0,752.0,114.0,-104.0,764.0,110.6,30" ws234_closeup_Montclair_Line_ballast_on_M3a_${TAGM}_main_sub $F $D
true
