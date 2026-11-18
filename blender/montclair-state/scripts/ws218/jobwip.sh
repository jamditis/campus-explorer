source scripts/ws218/srun218.sh
export SAMP=24 PCT=80 SKIRT=1 SUBR=scripts/ws218/subrend218.py
srun "-300,80,560,940" "110.0,560.0,260.0,-150.0,800.0,112.0,32" ws218_oblique_ChildrensCenter_merged_into_main_from_SE_ws218b_main_sub montclair_state.blend wip
srun "-260,-60,700,900" "-205.0,800.0,112.4,-168.0,815.0,113.5,28" ws218_eye_ChildrensCenter_entry_front_from_W_ws218b_main_sub montclair_state.blend wip
srun "-260,-60,700,900" "-105.0,745.0,111.8,-150.0,800.0,113.0,28" ws218_eye_ChildrensCenter_play_yard_side_from_SE_ws218b_main_sub montclair_state.blend wip
srun "-260,-60,700,900" "-186.0,792.0,116.5,-173.0,806.0,114.2,30" ws218_closeup_ChildrensCenter_W_gable_gutters_fixed_ws218b_main_sub montclair_state.blend wip
