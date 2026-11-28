# ws272 renders (#4c WS68 S-edge W of the Sprague grandstand lawn), terrain GN on (subrend234 default + KEEPMOD), crop259.
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40} GATE=${GATE:-4300}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws272a}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws272}; CH=${CH:-ws259/crop259.py}
[[ $ONLY == *1* ]] && srun "-300,-225,-160,-105" "-232.0,-162.0,150.0,-262.0,-128.0,119.0,30" ${P}_oblique_WS68_S_edge_W_of_grandstand_from_SE_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && srun "-300,-225,-160,-105" "-283.0,-131.5,119.1,-252.0,-133.0,119.2,30" ${P}_eye_Panzer_N_wall_lawn_from_W_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && srun "-300,-225,-160,-105" "-284.0,-121.0,121.7,-255.0,-134.0,119.0,30" ${P}_eye_WS68_S_edge_from_NW_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && srun "-300,-225,-160,-105" "-266.0,-124.5,123.5,-258.0,-135.0,118.6,30" ${P}_closeup_WS68_S_edge_at_Panzer_N_wall_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
