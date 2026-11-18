source scripts/ws213/srun213.sh
CU="-300,-235,-80,-20"
E1="-270.5,-60.0,126.4,-270.5,-42.0,125.0,30"
E2="-254.0,-63.0,131.5,-270.0,-45.0,124.5,30"
srun $CU "$E1" ws214_test_W35_E1_before montclair_state.blend test
srun $CU "$E2" ws214_test_W35_E2_before montclair_state.blend test
