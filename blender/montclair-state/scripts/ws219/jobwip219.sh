# ws219 final WIPs (main ws219e), subset renders, terrain GN on
source scripts/ws218/srun218.sh
F=montclair_state.blend; C="-300,-220,-90,-20"
srun "$C" "-232.0,-80.0,150.0,-256.0,-52.0,125.0,30" ws219_oblique_RHD_SE_crosswalk_corner_flush_curb_paint_mask_from_SE_ws219e_main_sub $F wip
srun "$C" "-250.5,-57.0,126.2,-258.0,-50.0,125.0,32" ws219_eye_College_Ave_curb_depressed_at_crosswalk_from_SE_ws219e_main_sub $F wip
srun "$C" "-258.0,-57.5,126.4,-254.8,-53.3,125.2,30" ws219_eye_crosswalk_corner_one_asphalt_tone_from_SW_ws219e_main_sub $F wip
srun "-270,-240,-65,-40" "-253.0,-55.6,125.9,-255.2,-53.0,125.2,30" ws219_closeup_flush_crosswalk_landing_nose_removed_painted_bars_ws219e_main_sub $F wip
