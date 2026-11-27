# ws256 WIPs/tests: Feliciano E walk N end / OSM path junction (f256a) + shadow tint S of the path (f256b)
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}"
export KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=${EXTRAJ:-$PWD/scripts/ws255/extra255.json}
F=${F:-montclair_state_ws256b.blend}; TAGM=${TAGM:-ws256b}; D=${D:-test}; ONLY=${ONLY:-1234}; P=${P:-ws256}; CH=${CH:-ws256/crop256.py}
[[ $ONLY == *1* ]] && srun "${CU1:--235,-140,120,230}" "${CAM1:--160.0,214.0,162.0,-192.0,186.0,137.5,30}" ${P}_oblique_Feliciano_E_walk_and_OSM_path_junction_from_NE_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *2* ]] && srun "${CU2:--215,-165,150,215}" "${CAM2:--190.6,196.0,140.6,-194.2,176.0,138.4,28}" ${P}_eye_Feliciano_E_walk_from_N_on_OSM_path_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *3* ]] && srun "${CU3:--215,-165,150,215}" "${CAM3:--189.6,171.0,138.35,-192.0,196.0,140.4,28}" ${P}_eye_walk_N_to_OSM_path_from_S_stair_top_${TAGM}_main_sub $F $D $CH
[[ $ONLY == *4* ]] && srun "${CU4:--215,-165,150,215}" "${CAM4:--185.0,199.0,143.0,-192.5,189.5,138.9,24}" ${P}_closeup_junction_paving_walk_OSM_path_${TAGM}_main_sub $F $D $CH
true
# police walk (f256c, M2c) views
[[ $ONLY == *5* ]] && EXTRAJ=$PWD/scripts/ws256/extra256.json srun "${CU5:--400,-300,-80,40}" "${CAM5:--316.0,-50.0,143.0,-347.0,-12.0,121.0,30}" ${P}_oblique_police_terrace_walk_merged_from_SE_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
[[ $ONLY == *6* ]] && EXTRAJ=$PWD/scripts/ws256/extra256.json srun "${CU6:--400,-300,-80,40}" "${CAM6:--333.0,-33.0,122.4,-350.0,-12.0,122.0,28}" ${P}_eye_police_terrace_walk_from_SE_${TAGM}_main_sub $F $D "ws239/upd239.py $CH"
true
