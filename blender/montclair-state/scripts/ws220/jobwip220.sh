# ws220 final WIPs (main ws220b), subset renders, terrain GN on
source scripts/ws218/srun218.sh
F=montclair_state.blend; C="-300,-220,-90,-20"
srun "$C" "-232.0,-80.0,150.0,-256.0,-52.0,125.0,30" ws220_oblique_RHD_SE_Kasser_corner_curb_jog_closed_from_SE_ws220b_main_sub $F wip
srun "$C" "-243.0,-60.0,127.3,-249.0,-54.5,125.6,30" ws220_eye_College_Ave_continuous_curb_at_Kasser_landing_from_SE_ws220b_main_sub $F wip
srun "$C" "-262.0,-57.8,126.8,-248.0,-54.0,125.8,30" ws220_eye_College_Ave_curb_line_from_W_crosswalk_ws220b_main_sub $F wip
srun "$C" "-249.0,-58.5,131.0,-249.0,-54.5,125.6,35" ws220_closeup_curb_jog_return_and_grass_verge_ws220b_main_sub $F wip
