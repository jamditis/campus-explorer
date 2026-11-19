# ws233 four WIPs (W53o Stone Hall ground-floor windows raised onto a brick base above grade), subset, terrain GN on, KEEPMOD paving drapes on
source scripts/ws226/srun226.sh
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM}" SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED WS229_SE_south_edge_apron_UNVERIFIED WS230_NE_east_gap_fill_3DEP_UNVERIFIED"
F=${F:-montclair_state_ws233b.blend}; TAGM=${TAGM:-ws233b}; D=${D:-wip}; ONLY=${ONLY:-1234}
[[ $ONLY == *1* ]] && srun "110,190,190,300" "182.0,196.0,162.0,148.0,248.0,138.0,28" ws233_oblique_Stone_Hall_E_W53o_from_SE_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "110,170,180,245" "151.0,228.0,138.6,134.0,198.0,137.4,30" ws233_eye_Stone_Hall_E_walk_W53o_from_NE_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "120,190,195,270" "163.0,221.0,138.3,146.0,236.0,138.4,30" ws233_eye_Stone_Hall_ESE_wall_W53o_from_SE_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "135,165,215,245" "152.6,226.4,137.6,148.6,231.2,138.2,35" ws233_closeup_Stone_Hall_sills_W53o_${TAGM}_main_sub $F $D
true
