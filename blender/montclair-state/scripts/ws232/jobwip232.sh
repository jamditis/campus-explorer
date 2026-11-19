# ws232 four WIPs (W53b CELS/Calcia NE-corner walk overlays snapped onto the draped walks), subset, terrain GN on, KEEPMOD paving drapes on
source scripts/ws226/srun226.sh
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM}" SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED WS229_SE_south_edge_apron_UNVERIFIED WS230_NE_east_gap_fill_3DEP_UNVERIFIED"
F=${F:-montclair_state_ws232b.blend}; TAGM=${TAGM:-ws232b}; D=${D:-wip}; ONLY=${ONLY:-1234}
[[ $ONLY == *1* ]] && srun "80,175,160,262" "100.0,160.0,165.0,135.0,210.0,137.0,28" ws232_oblique_CELS_NE_walks_W53b_from_SW_${TAGM}_main_sub $F $D
[[ $ONLY == *2* ]] && srun "105,165,170,250" "128.0,178.0,138.9,142.0,214.0,137.5,30" ws232_eye_CELS_NE_walk_W53b_from_S_${TAGM}_main_sub $F $D
[[ $ONLY == *3* ]] && srun "110,170,180,245" "151.0,228.0,138.6,134.0,198.0,137.4,30" ws232_eye_CELS_NE_walk_W53b_from_NE_${TAGM}_main_sub $F $D
[[ $ONLY == *4* ]] && srun "120,150,180,215" "131.0,189.0,138.9,137.0,203.0,137.3,30" ws232_closeup_CELS_walk_joints_W53b_${TAGM}_main_sub $F $D
true
