# ws276 renders: Sprague Library east door (ofj-ceinteriors door 1, -50.20, 34.99, sill 137.90), terrain GN on (subrend234 + KEEPMOD), crop259.
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-30} GATE=${GATE:-6000}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws276a}; D=${D:-test}; ONLY=${ONLY:-123}; P=${P:-ws276}; CH=${CH:-ws259/crop259.py}
[[ $ONLY == *1* ]] && srun "${CULLB:--80,-20,10,60}" "-36.0,31.8,139.6,-50.2,35.0,139.2,30" ${P}_eye_Sprague_E_door_from_E_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && srun "${CULLB:--80,-20,10,60}" "-40.0,20.0,141.0,-50.4,35.0,139.0,32" ${P}_eye_Sprague_E_door_from_SE_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && srun "${CULLB:--80,-20,10,60}" "-46.6,34.0,139.3,-56.0,35.6,138.8,24" ${P}_closeup_Sprague_E_door_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
