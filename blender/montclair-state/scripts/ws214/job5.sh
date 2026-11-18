source scripts/ws213/srun213.sh
CU="-275,-235,-75,-40"
C4="-259.5,-56.8,126.5,-255.3,-52.8,125.2,32"
C5="-262.5,-52.5,126.6,-254.0,-58.5,125.1,28"
srun $CU "$C4" ws214_test_W36N_C4_before montclair_state.blend test
srun $CU "$C4" ws214_test_W36N_C4_after montclair_state.blend test ws214/fix214d.py
srun $CU "$C5" ws214_test_W36N_C5_after montclair_state.blend test ws214/fix214d.py
