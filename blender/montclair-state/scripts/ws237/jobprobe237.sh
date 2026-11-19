source scripts/ws226/srun226.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km} M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws235/extra235.json
cd /workspace/nj-scenes/montclair-state
FILE=$PWD/${F:-montclair_state.blend} CHAIN="${CH:-ws237/probe237a.py}" CULL="${C:--480,-150,-130,540}" WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws234/subrend234.py 2>&1 | grep -E "F237|P237|SUB205|MEM|VmHWM|Trace|rror|WATCH"
