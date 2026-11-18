source scripts/ws212/srun212.sh
CE="-257.0,-53.0,126.3,-300.0,-47.0,124.6,24"; CUE="-335,-225,-95,0"
export SAMP=24 PCT=80
NOTERRAIN=1 srun $CUE "$CE" ws212_eye_CollegeAve_by_deck_BEFORE_old_sub_renderer montclair_state.blend test
srun $CUE "$CE" eye_CollegeAve_by_RedHawk_deck_looking_W_true_terrain_ws211b_main_sub212 montclair_state.blend wip
