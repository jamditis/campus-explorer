# ws274 renders (pattern of ws270/jobwip270.sh): College Ave N curb + gutter. Terrain GN on (subrend234 + KEEPMOD), crop259.
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40} GATE=${GATE:-4300}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
export EXTRA="WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED WS269_W72b_Lot33_tree_island_curb_ortho2020_UNVERIFIED WS269_W72b_Lot33_tree_island_mulch_UNVERIFIED WS269_tree_Lot33_island_LiDAR2023_h12m_UNVERIFIEDspecies WS274_CollegeAve_N_curb_ortho2020_UNVERIFIED WS274_CollegeAve_N_gutter_pan_UNVERIFIED"
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws274a}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws274}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "-410,-300,-90,30" "-392.0,-66.0,136.0,-360.0,-24.0,120.0,32" ${P}_oblique_CollegeAve_N_curb_from_SW_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "-410,-300,-80,40" "-325.0,-31.0,123.1,-360.0,-22.0,120.6,30" ${P}_eye_College_Ave_N_curb_and_hatch_from_E_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EP srun "-410,-300,-80,40" "-387.0,-24.0,119.7,-350.0,-21.5,120.0,30" ${P}_eye_College_Ave_N_curb_from_W_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && EXTRAJ=$EP srun "-400,-300,-80,40" "-361.5,-25.0,120.6,-366.0,-20.6,119.3,30" ${P}_closeup_N_curb_gutter_police_lawn_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
