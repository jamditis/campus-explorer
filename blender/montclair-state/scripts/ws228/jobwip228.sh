# ws228 before/after test + four WIPs (W53d SE east edge + apex slivers re-gridded to dtm_1m), subset, terrain GN on
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED"
F=${F:-montclair_state_ws228d.blend}; TAGM=${TAGM:-ws228d}
OBL="150.0,-290.0,140.0,230.0,-150.0,88.0,28"
if [ -n "$TEST" ]; then
srun "120,250,-250,-30" "$OBL" ws228_test_W53d_east_edge_oblique_from_SW_BEFORE_ws227g_sub montclair_state.blend test
srun "120,250,-250,-30" "$OBL" ws228_test_W53d_east_edge_oblique_from_SW_AFTER_${TAGM}_sub $F test
exit 0; fi
srun "120,250,-250,-30" "$OBL" ws228_oblique_SE_east_edge_W53d_from_SW_${TAGM}_main_sub $F wip
srun "180,250,-220,-90" "215.0,-150.0,94.9,245.0,-170.0,87.5,30" ws228_eye_SE_east_edge_W53d_from_W_${TAGM}_main_sub $F wip
srun "200,250,-230,-40" "238.0,-60.0,92.3,240.0,-200.0,86.5,30" ws228_eye_SE_east_edge_W53d_from_N_${TAGM}_main_sub $F wip
srun "200,250,-250,-215" "225.0,-232.0,90.2,244.0,-246.0,85.5,32" ws228_closeup_A1_corner_W53d_${TAGM}_main_sub $F wip
