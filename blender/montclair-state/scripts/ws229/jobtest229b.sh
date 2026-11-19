# ws229 W53h before/after (south edge apron), subset, terrain GN on
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED WS229_SE_south_edge_apron_UNVERIFIED"
CAMS="200.0,-236.0,93.5,165.0,-258.0,89.0,30"
srun "120,250,-270,-200" "$CAMS" ws229_test_W53h_south_edge_eye_from_NE_BEFORE_ws229b_sub montclair_state_ws229b.blend test
srun "120,250,-270,-200" "$CAMS" ws229_test_W53h_south_edge_eye_from_NE_AFTER_ws229c_sub montclair_state_ws229c.blend test
