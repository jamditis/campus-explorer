# ws230 W53j before/after tests (NE east-edge gap fill + strip re-height to 3DEP 1 m), subset, terrain GN on
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED WS229_SE_south_edge_apron_UNVERIFIED WS230_NE_east_gap_fill_3DEP_UNVERIFIED"
F=${F:-montclair_state_ws230a.blend}; TAGM=${TAGM:-ws230a}
EYE="205.0,60.0,100.8,248.0,150.0,97.5,30"
OBL="120.0,-30.0,165.0,240.0,140.0,98.0,28"
srun "150,280,0,270" "$EYE" ws230_test_W53j_eye_from_SW_BEFORE_ws229d_sub montclair_state.blend test
srun "150,280,0,270" "$EYE" ws230_test_W53j_eye_from_SW_AFTER_${TAGM}_sub $F test
srun "120,280,-40,270" "$OBL" ws230_test_W53j_oblique_from_SW_BEFORE_ws229d_sub montclair_state.blend test
srun "120,280,-40,270" "$OBL" ws230_test_W53j_oblique_from_SW_AFTER_${TAGM}_sub $F test
