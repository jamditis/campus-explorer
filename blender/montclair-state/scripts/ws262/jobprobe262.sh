source scripts/ws262/srun262.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws262/extra262.json}
srun "$CU" "-200,-200,140,-200,-201,120,30" probe_$PN ${F:-montclair_state.blend} test $CH
