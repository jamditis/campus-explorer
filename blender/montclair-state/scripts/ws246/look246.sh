#!/bin/bash
# ws246 lite look render (no skirt/M3b, terrain GN on for Terrain/WS60 only) for small close views under tight memory
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}" KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt}" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws246/extra246.json}
srun "$C" "$CAM" "$N" ${F:-montclair_state_ws246a.blend} ${D:-test} ws239/upd239.py
