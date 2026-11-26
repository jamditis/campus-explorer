#!/bin/bash
# ws246 small-cull probe (subrend234, terrain GN on). usage: C=x0,x1,y0,y1 CH=ws246/x.py [PG=...] bash scripts/ws246/probe246.sh
cd /workspace/nj-scenes/montclair-state
export HIDE=BD_farfield KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" EXTRAJ=${EXTRAJ:-$PWD/scripts/ws246/extra246.json}
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-2800} ] && ! pgrep -x blender >/dev/null; do sleep 3; done
FILE=$PWD/${F:-montclair_state.blend} CHAIN="$CH" CULL="$C" WD_MIN=${WDM:-1200} bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws234/subrend234.py 2>&1 | grep -E "P246|SUB205|Trace|rror|WATCH"
