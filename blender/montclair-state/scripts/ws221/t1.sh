source scripts/ws218/srun218.sh
C="-300,-220,-90,-20"
srun "$C" "-249.0,-58.5,131.0,-249.5,-54.8,125.6,35" ws221_test_W40_close_from_S_ws221b ${F:-montclair_state_ws221b.blend} test
srun "$C" "-243.0,-60.0,127.3,-249.0,-54.5,125.6,30" ws221_test_W40_eye_from_SE_ws221b ${F:-montclair_state_ws221b.blend} test
