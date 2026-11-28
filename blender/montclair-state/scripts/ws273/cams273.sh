# ws273 renders (#4a/#4b Sprague grandstand lawn + lot-pocket strip), terrain GN on (subrend234 + KEEPMOD), crop259, tight CULL.
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-30} GATE=${GATE:-7000}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws273a}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws273}; CH=${CH:-ws259/crop259.py}
[[ $ONLY == *1* ]] && srun "${CULLB:--266,-226,-140,-100}" "-236.0,-190.0,190.0,-246.0,-118.0,121.0,35" ${P}_oblique_Sprague_grandstand_lawn_and_lot_pocket_from_S_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && srun "${CULLB:--266,-226,-140,-100}" "-231.0,-131.0,125.6,-252.0,-110.0,123.8,32" ${P}_eye_grandstand_lawn_to_lot_from_SE_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && srun "${CULLB:--266,-226,-140,-100}" "-271.0,-104.0,124.8,-244.0,-122.0,124.0,32" ${P}_eye_grandstand_lawn_from_NW_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && srun "${CULLB:--266,-226,-140,-100}" "-238.0,-117.5,125.6,-244.0,-108.0,123.7,30" ${P}_closeup_lot_S_edge_lawn_strip_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
