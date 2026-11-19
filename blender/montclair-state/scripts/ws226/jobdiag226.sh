# W53 diagnosis aerials (before = ws225a main, after = ws226a), subset renders, terrain GN on
source scripts/ws218/srun218.sh
srun "110,250,-40,250" "95.0,-95.0,215.0,190.0,100.0,105.0,30" ws226_test_W53_east_aerial_from_SW_BEFORE_ws225a_sub montclair_state.blend test
srun "110,250,-40,250" "95.0,-95.0,215.0,190.0,100.0,105.0,30" ws226_test_W53_east_aerial_from_SW_AFTER_ws226a_sub montclair_state_ws226a.blend test
