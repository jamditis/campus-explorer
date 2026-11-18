source scripts/ws212/srun212.sh
CS="-212.0,-102.0,150.0,-240.0,-79.0,126.0,30"; CU="-320,-170,-130,-10"
CE="-257.0,-53.0,126.3,-300.0,-47.0,124.6,24"; CUE="-335,-225,-95,0"
export SAMP=24 PCT=80
NOTERRAIN=1 srun $CU "$CS" ws212_SE_oblique_BEFORE_old_sub_renderer montclair_state.blend test
srun $CU "$CS" oblique_accessible_lot_CollegeAve_RedHawk_from_SE_true_terrain_ws211b_main_sub212 montclair_state.blend wip
NOTERRAIN=1 srun $CUE "$CE" ws212_eye_CollegeAve_by_deck_BEFORE_old_sub_renderer montclair_state.blend test
srun $CUE "$CE" eye_CollegeAve_by_RedHawk_deck_looking_W_true_terrain_ws211b_main_sub212 montclair_state.blend wip
