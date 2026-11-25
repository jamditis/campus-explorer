# ws240 tests: W12c CCOM apron S-edge corner / walk fold (eye from SW, ws209 camera) on a given file
source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km} WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws240/extra240.json
F=${F:-montclair_state_ws240c.blend}; TAGM=${TAGM:-ws240c}
srun "-20,40,-70,-10" "${CAMT:-0.5,-44.5,136.4,7.5,-37.5,135.3,35}" ws240_test_W12c_CCOM_apron_walk_from_SW_${TAGM} $F test ws239/upd239.py
