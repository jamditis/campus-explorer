source scripts/ws217/srun217.sh
export SAMP=16 PCT=60
srun "-300,-235,-80,-20" "-250.0,-50.5,126.4,-253.5,-46.5,125.3,32" ws217_test_W38_closeup_after_rev3 montclair_state_ws217a.blend test "ws217/fix217d.py"
