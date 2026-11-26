# ws248 low-memory probe render: tight cull + soccer-only extras (extra248_small.json); terrain GN on.
source scripts/ws246/srun246.sh
export HIDE="BD_farfield" KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws248/extra248_small.json}
GATE=${GATE:-2700} PCT=${PCT:-35} SAMP=${SAMP:-8} srun "$C" "$CAM" "$TAG" "${F:-montclair_state.blend}" "${D:-test}" "${CH:-}"
