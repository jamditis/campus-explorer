# ws251 final WIPs (W63b passage) from ws251b
cd /workspace/nj-scenes/montclair-state
export F=montclair_state_ws251b.blend TAGM=ws251b D=wip P=ws251
CAM1="-150.0,105.0,175.0,-188.0,160.0,135.5,30" CU1="-240,-90,100,250" ONLY=1 bash scripts/ws251/jobwip251.sh
ONLY=3 bash scripts/ws251/jobwip251.sh
source scripts/ws246/srun246.sh
export HIDE="${HIDE:-BD_farfield}" KEEPMOD="Roads_OSM Footpaths_OSM Context_skirt_3DEP_ortho_4km WS60_terrain_edge_apron_LiDAR_to_skirt" SUBR=scripts/ws234/subrend234.py EXTRAJ=$PWD/scripts/ws251/extra251.json
srun "-215,-150,120,230" "-188.0,137.0,138.7,-187.0,175.0,137.5,28" ws251_eye_Feliciano_Dickson_passage_from_S_lowered_to_LiDAR_ws251b_main_sub $F wip
srun "-200,-170,140,175" "-190.0,151.0,136.3,-182.5,158.0,136.0,32" ws251_closeup_Dickson_NW_corner_base_on_lowered_passage_ground_ws251b_main_sub $F wip
echo ALLDONE
