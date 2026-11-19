source scripts/ws218/srun218.sh
C="-300,-220,-90,-20"; F=${F:-montclair_state_ws223a.blend}; TG=${TAG:-ws223a}
srun "$C" "-247.2,-56.5,126.9,-248.7,-53.6,125.7,30" ws223_test_curb_return_landing_from_S_$TG $F test
srun "$C" "-247.0,-51.2,126.6,-248.6,-52.95,125.85,32" ws223_test_curb_return_landing_from_NE_$TG $F test
