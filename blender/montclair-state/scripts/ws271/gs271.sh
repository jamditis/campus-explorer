# ws271 Sprague grandstand lawn (#4) subset renders, terrain GN on (subrend234 default), crop259, tight CULL around the lawn.
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-30} GATE=${GATE:-8000}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws271a}; D=${D:-test}; ONLY=${ONLY:-12}; P=${P:-ws271}; CH=${CH:-ws259/crop259.py}
[[ $ONLY == *1* ]] && srun "-262,-212,-172,-112" "-206.0,-178.0,150.0,-240.0,-140.0,121.5,32" ${P}_oblique_Sprague_grandstand_lawn_from_SE_high_${TAGM}_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && srun "-262,-212,-172,-112" "-236.0,-190.0,190.0,-238.0,-130.0,121.0,35" ${P}_oblique_Sprague_grandstand_lawn_from_S_high_${TAGM}_sub $F $D "ws239/upd239.py $CH"
true
