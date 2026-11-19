source scripts/ws216/srun216.sh
CU="-300,-235,-80,-20"
srun $CU "-250.5,-57.0,126.2,-258.0,-50.0,125.0,32" ws216_test_W35c_E5_after_a montclair_state.blend test ws216/fix216a.py
srun $CU "-252.0,-52.5,126.3,-262.0,-46.5,125.0,32" ws216_test_W35c_E4_after_a montclair_state.blend test ws216/fix216a.py
