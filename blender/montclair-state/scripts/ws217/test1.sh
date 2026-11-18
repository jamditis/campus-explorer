source scripts/ws217/srun217.sh
export SAMP=16 PCT=60
srun "-300,-235,-80,-20" "-262.0,-53.0,126.0,-267.0,-45.5,124.6,35" ws217_test_W35e_closeup_after montclair_state.blend test ws217/fix217a.py
srun "-300,-235,-80,-20" "-252.0,-52.5,126.3,-262.0,-46.5,125.0,32" ws217_test_W35e_eyeE_after montclair_state.blend test ws217/fix217a.py
