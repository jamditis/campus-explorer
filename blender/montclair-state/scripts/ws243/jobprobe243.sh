cd /workspace/nj-scenes/montclair-state
echo "$(date +%T) START"
export HIDE="${HIDE:-BD_farfield}" KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" EXTRAJ=${EXTRAJ:-$PWD/scripts/ws241/extra241.json}
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-3000} ] && ! pgrep -x blender >/dev/null; do sleep 3; done
FILE=$PWD/${F:-montclair_state.blend} CHAIN="${CH:-ws243/probe243a.py}" CULL="${C}" WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws234/subrend234.py 2>&1 | grep -E "P243|P242|P241|SUB205|Trace|rror|WATCH"
