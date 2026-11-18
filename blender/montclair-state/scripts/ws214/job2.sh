source scripts/ws213/srun213.sh
CU="-275,-235,-75,-40"
C1="-259.0,-53.5,126.6,-255.5,-58.5,124.9,30"
C2="-258.5,-60.5,126.3,-255.0,-56.5,125.0,35"
C3="-253.0,-63.5,126.2,-254.5,-58.5,125.0,32"
srun $CU "$C1" ws214_test_W36_C1_after2 montclair_state.blend test ws214/fix214a.py
srun $CU "$C2" ws214_test_W36_C2_after2 montclair_state.blend test ws214/fix214a.py
srun $CU "$C3" ws214_test_W36_C3_before montclair_state.blend test
srun $CU "$C3" ws214_test_W36_C3_after2 montclair_state.blend test ws214/fix214a.py
