source scripts/ws213/srun213.sh
CU="-300,-235,-80,-20"
E1="-270.5,-60.0,126.4,-270.5,-42.0,125.0,30"
E2="-254.0,-63.0,131.5,-270.0,-45.0,124.5,30"
E3="-262.0,-53.0,126.0,-267.0,-45.5,124.6,35"
srun $CU "$E2" ws214_test_W35_E2_after_c montclair_state.blend test ws214/fix214c.py
srun $CU "$E3" ws214_test_W35_E3_before montclair_state.blend test
srun $CU "$E3" ws214_test_W35_E3_after_c montclair_state.blend test ws214/fix214c.py
