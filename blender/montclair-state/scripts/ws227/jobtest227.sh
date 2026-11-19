# ws227 W53c before/after: SE corner oblique (subset, terrain GN on, subrend226)
source scripts/ws226/srun226.sh
export SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED"
srun "90,250,-250,-30" "80.0,-270.0,150.0,200.0,-140.0,93.0,28" ws227_test_W53c_SE_corner_oblique_from_SW_BEFORE_ws226f_sub montclair_state.blend test
srun "90,250,-250,-30" "80.0,-270.0,150.0,200.0,-140.0,93.0,28" ws227_test_W53c_SE_corner_oblique_from_SW_AFTER_ws227a_sub montclair_state_ws227a.blend test
