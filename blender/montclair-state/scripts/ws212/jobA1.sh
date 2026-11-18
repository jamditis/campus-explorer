source scripts/ws212/srun212.sh
CS="-212.0,-102.0,150.0,-240.0,-79.0,126.0,30"; CU="-320,-170,-130,-10"
srun $CU "$CS" ws212_SE_oblique_alloff_sub montclair_state.blend test
KEEPALL=1 srun $CU "$CS" ws212_SE_oblique_KEEPALL_full_terrain montclair_state.blend test
