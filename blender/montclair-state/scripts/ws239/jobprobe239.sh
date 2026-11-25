cd /workspace/nj-scenes/montclair-state
export HIDE="${HIDE:-BD_farfield}" KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" EXTRAJ=$PWD/scripts/ws239/extra239.json
FILE=$PWD/${F:-montclair_state_ws239b.blend} CHAIN="${CH:-ws239/probe239e.py}" CULL="${C:--480,-130,-150,540}" WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws234/subrend234.py 2>&1 | grep -E "P239|P237|SUB205|Trace|rror|WATCH"
