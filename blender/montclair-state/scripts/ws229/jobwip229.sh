# ws229 four WIPs (W53g QI band, W53e ortho registration, W53h south edge apron) + close-up BEFORE test; subset, terrain GN on
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED WS229_SE_south_edge_apron_UNVERIFIED"
F=${F:-montclair_state_ws229d.blend}; TAGM=${TAGM:-ws229d}
CLO="192.0,-58.0,97.5,208.0,-44.0,94.1,32"
srun "120,250,-250,-30" "150.0,-290.0,140.0,230.0,-150.0,88.0,28" ws229_oblique_SE_corner_W53e_g_h_from_SW_${TAGM}_main_sub $F wip
srun "200,250,-230,-40" "238.0,-60.0,92.3,240.0,-200.0,86.5,30" ws229_eye_SE_street_W53e_from_N_${TAGM}_main_sub $F wip
srun "120,250,-270,-200" "200.0,-236.0,93.5,165.0,-258.0,89.0,30" ws229_eye_south_edge_apron_W53h_from_NE_${TAGM}_main_sub $F wip
srun "150,280,-90,-20" "$CLO" ws229_closeup_QI_band_W53g_${TAGM}_main_sub $F wip
