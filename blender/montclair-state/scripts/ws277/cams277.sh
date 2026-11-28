# ws277 renders: Alumni House (OSM 232846660, about -359, -272), terrain GN on (subrend234 + KEEPMOD), crop259.
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-30} GATE=${GATE:-6000}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws277a}; D=${D:-test}; ONLY=${ONLY:-123}; P=${P:-ws277}; CH=${CH:-ws259/crop259.py}
[[ $ONLY == *1* ]] && srun "${CULLB:--400,-310,-310,-230}" "-332.0,-246.0,118.4,-359.0,-272.0,118.5,30" ${P}_eye_Alumni_House_from_Normal_Ave_NE_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && srun "${CULLB:--400,-310,-310,-230}" "-330.0,-235.0,145.0,-359.0,-272.0,118.0,32" ${P}_oblique_Alumni_House_from_NE_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
