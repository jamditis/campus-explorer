# ws231 four WIPs (W53l N woods path + QI pit, W53k NE street east end, W53m SE street end), subset, terrain GN on
source scripts/ws226/srun226.sh
export KEEPMOD="${KEEPMOD:-Roads_OSM Footpaths_OSM}" SUBR=scripts/ws226/subrend226.py EXTRA="WS226_east_patch_seam_backing_UNVERIFIED WS229_SE_south_edge_apron_UNVERIFIED WS230_NE_east_gap_fill_3DEP_UNVERIFIED"
F=${F:-montclair_state_ws231b.blend}; TAGM=${TAGM:-ws231b}; D=${D:-wip}
srun "110,280,110,270" "120.0,150.0,170.0,195.0,232.0,112.0,28" ws231_oblique_N_NE_edge_W53k_W53l_from_SW_${TAGM}_main_sub $F $D
srun "130,200,195,270" "159.0,226.0,138.3,164.5,247.0,136.0,30" ws231_eye_N_woods_path_W53l_from_S_${TAGM}_main_sub $F $D
srun "185,280,150,240" "221.0,190.0,106.9,242.0,199.0,104.0,30" ws231_eye_NE_street_east_end_W53k_from_W_${TAGM}_main_sub $F $D
srun "215,280,-65,5" "238.5,-35.0,92.3,249.0,-28.0,89.3,30" ws231_closeup_SE_street_end_on_apron_W53m_${TAGM}_main_sub $F $D
