source scripts/ws218/srun218.sh
C="0,50,330,370"
srun "$C" "25.0,340.0,140.8,25.0,351.5,139.0,30" ws220_test_Lot38_stalls_eye_BEFORE_ws219e montclair_state.blend test
srun "$C" "25.0,340.0,140.8,25.0,351.5,139.0,30" ws220_test_Lot38_stalls_eye_AFTER_ws220a montclair_state_ws220a.blend test
