# ws225 final WIPs (main ws225a: W47 down-facing ground sheets flipped), subset renders, terrain GN on
source scripts/ws218/srun218.sh
F=montclair_state.blend
srun "-160,-70,280,380" "-88.0,298.0,166.0,-117.0,331.0,141.0,28" ws225_oblique_Annex_W_asphalt_plaza_normals_up_from_SE_ws225a_main_sub $F wip
srun "-80,-10,10,90" "-44.0,26.0,139.7,-44.0,55.0,138.1,30" ws225_eye_CafeDiem_patio_pavers_from_S_ws225a_main_sub $F wip
srun "-20,40,-60,0" "20.0,-45.0,137.6,6.0,-30.0,135.8,30" ws225_eye_CCOM_dock_apron_from_SE_ws225a_main_sub $F wip
srun "-95,-40,-70,-35" "-61.0,-52.0,136.4,-64.0,-54.5,134.9,34" ws225_closeup_Cole_Morehead_walk_brick_edging_ws225a_main_sub $F wip
