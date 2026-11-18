source scripts/ws217/srun217.sh
export SAMP=16 PCT=60
PROBE_EXIT=1 SAMP=4 PCT=10 srun "-300,-235,-80,-20" "-252.0,-52.5,126.3,-262.0,-46.5,125.0,32" ws217_probeE_after montclair_state.blend test "ws217/fix217d.py ws217/probe217e.py"
srun "-330,-190,-130,-10" "-236.0,-78.0,150.0,-258.0,-56.0,125.0,30" ws217_test_W38_oblique_after montclair_state.blend test "ws217/fix217d.py"
srun "-300,-235,-80,-20" "-250.5,-57.0,126.2,-258.0,-50.0,125.0,32" ws217_test_W38_eyeSE_after montclair_state.blend test "ws217/fix217d.py"
