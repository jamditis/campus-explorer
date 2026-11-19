# ws229 before/after tests (W53e ortho UV registration + W53g QI patch band), subset, terrain GN on
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED"
F=${F:-montclair_state_ws229b.blend}; TAGM=${TAGM:-ws229b}
srun "200,250,-230,-40" "238.0,-60.0,92.3,240.0,-200.0,86.5,30" ws229_test_W53e_eye_from_N_BEFORE_ws228f_sub montclair_state.blend test
srun "200,250,-230,-40" "238.0,-60.0,92.3,240.0,-200.0,86.5,30" ws229_test_W53e_eye_from_N_AFTER_${TAGM}_sub $F test
srun "120,250,-250,-30" "150.0,-290.0,140.0,230.0,-150.0,88.0,28" ws229_test_SE_oblique_from_SW_AFTER_${TAGM}_sub $F test
