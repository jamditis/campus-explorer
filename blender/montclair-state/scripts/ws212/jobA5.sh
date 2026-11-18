source scripts/ws212/srun212.sh
CE="-278.0,-50.5,126.2,-238.0,-60.0,125.4,24"; CUE="-320,-200,-110,0"
export SAMP=24 PCT=80
NOTERRAIN=1 srun $CUE "$CE" ws212_eye_CollegeAve_E_past_deck_BEFORE_old_sub_renderer montclair_state.blend test
srun $CUE "$CE" eye_CollegeAve_looking_E_past_RedHawk_deck_to_accessible_lot_true_terrain_ws211b_main_sub212 montclair_state.blend wip
