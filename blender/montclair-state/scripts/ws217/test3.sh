source scripts/ws217/srun217.sh
export SAMP=16 PCT=60
C="ws217/fix217a.py ws217/fix217b.py ws217/fix217c.py"
srun "-300,-235,-80,-20" "-256.0,-58.5,126.4,-262.0,-48.5,124.8,30" ws217_test_W40_eyeS_after montclair_state.blend test "$C"
srun "-300,-235,-80,-20" "-252.0,-52.5,126.3,-262.0,-46.5,125.0,32" ws217_test_W40_eyeE_after montclair_state.blend test "$C"
PROBE_EXIT=1 SAMP=4 PCT=10 srun "-300,-235,-80,-20" "-252.0,-52.5,126.3,-262.0,-46.5,125.0,32" ws217_probe_W40_after montclair_state.blend test "$C ws217/probe217d.py"
