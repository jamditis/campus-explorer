C="-250,-216,-112,-88"; CU="-228.0,-108.0,128.2,-236.0,-99.0,124.2,28"
run $C "$CU" cut_ws201_W19_closeup_S_bay_seam_BEFORE_ws200a montclair_state.blend test
IMP=$PWD/scripts/ws201/fix201b_coords_np2.npz run $C "$CU" cut_ws201_W19_closeup_S_bay_seam_AFTER_fix201b montclair_state.blend test ws201/imp201b.py
