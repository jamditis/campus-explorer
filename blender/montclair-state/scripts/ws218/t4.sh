source scripts/ws218/srun218.sh
SKIRT=1 SUBR=scripts/ws218/subrend218.py srun "-240,0,150,340" "-10.0,170.0,185.0,-140.0,280.0,150.0,24" ws218_test_M2a_UH_wide_from_SE_r2 montclair_state_ws218a.blend test
SKIRT=1 SUBR=scripts/ws218/subrend218.py srun "-260,-60,700,900" "-90.0,760.0,135.0,-160.0,812.0,113.0,26" ws218_test_M2a_ChildrensCenter_from_E montclair_state_ws218a.blend test
