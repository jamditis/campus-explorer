# ws270 renders (pattern of ws269/jobwip269.sh); F defaults to main. Terrain GN on (KEEPMOD), crop259.
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40} GATE=${GATE:-4300}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
export EXTRA="WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED WS269_W72b_Lot33_tree_island_curb_ortho2020_UNVERIFIED WS269_W72b_Lot33_tree_island_mulch_UNVERIFIED WS269_tree_Lot33_island_LiDAR2023_h12m_UNVERIFIEDspecies"
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws270a}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws270}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "-410,-300,-90,30" "-392.0,-78.0,138.0,-350.0,-36.0,120.0,32" ${P}_oblique_CollegeAve_Lot33_regraded_from_SW_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "-410,-300,-90,30" "-378.0,-31.0,120.3,-340.0,-39.0,120.6,30" ${P}_eye_CollegeAve_from_Carlisle_Rd_W_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EP srun "-410,-300,-80,40" "-336.0,-27.5,122.6,-372.0,-20.5,120.6,30" ${P}_eye_College_Ave_N_curb_from_E_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && EXTRAJ=$EP srun "-400,-300,-80,40" "-359.0,-27.0,121.0,-364.5,-20.5,119.8,30" ${P}_closeup_N_curb_police_lawn_foot_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
