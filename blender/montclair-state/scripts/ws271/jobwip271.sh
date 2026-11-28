# ws271 renders (pattern of ws270/jobwip270.sh); F defaults to main. Terrain GN on (KEEPMOD), crop259.
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40} GATE=${GATE:-4300}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
export EXTRA="WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED WS269_W72b_Lot33_tree_island_curb_ortho2020_UNVERIFIED WS269_W72b_Lot33_tree_island_mulch_UNVERIFIED WS269_tree_Lot33_island_LiDAR2023_h12m_UNVERIFIEDspecies"
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws271a}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws271}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "-410,-300,-90,30" "-392.0,-78.0,138.0,-350.0,-36.0,120.0,32" ${P}_oblique_CollegeAve_Lot33_SW_corner_from_SW_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "-410,-300,-80,40" "-336.0,-27.5,122.6,-372.0,-20.5,120.6,30" ${P}_eye_College_Ave_N_edge_walk_W_end_from_E_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EP srun "-410,-300,-80,40" "-366.0,-45.5,120.8,-388.0,-38.0,118.8,30" ${P}_eye_Lot33_S_edge_to_SW_corner_from_SE_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && EXTRAJ=$EP srun "-400,-300,-80,40" "-380.5,-48.0,121.6,-382.0,-40.5,118.5,30" ${P}_closeup_SW_corner_S_edge_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
