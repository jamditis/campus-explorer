# ws268 renders (pattern of ws267/jobwip267.sh); F defaults to main
source scripts/ws263/srun263.sh
export HIDE="${HIDE:-BD_farfield}" CROPM=${CROPM:-40} GATE=${GATE:-4300}
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt gd_grass_police_lawn_points" SUBR=scripts/ws234/subrend234.py
F=${F:-montclair_state.blend}; TAGM=${TAGM:-ws267c}; D=${D:-test}; ONLY=${ONLY:-1}; P=${P:-ws268}; CH=${CH:-ws259/crop259.py}
EP=$PWD/scripts/ws262/extra262p.json
[[ $ONLY == *1* ]] && EXTRAJ=$EP srun "${CU1:--410,-300,-90,30}" "${CAM1:--330.0,8.0,140.0,-362.0,-35.0,119.0,30}" ${P}_oblique_ground_S_SW_of_police_from_NE_high_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *2* ]] && EXTRAJ=$EP srun "${CU2:--410,-300,-90,30}" "${CAM2:--372.0,-45.0,121.0,-345.0,-5.0,123.5,32}" ${P}_eye_police_plaza_from_SW_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *3* ]] && EXTRAJ=$EP srun "${CU3:--400,-300,-80,40}" "${CAM3:--333.0,3.0,125.1,-341.0,-4.0,124.2,26}" ${P}_eye_police_S_from_NE_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *4* ]] && EXTRAJ=$EP srun "${CU4:--400,-300,-80,40}" "${CAM4:--350.0,-22.0,123.5,-358.0,-32.0,119.5,40}" ${P}_closeup_ground_SW_of_police_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
