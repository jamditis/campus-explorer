#!/bin/bash
# Session ei WIPs
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-24}
run() { free -m | head -2; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_ei.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|SOFT|VIEW|hid trees|Error"; }
for v in ${VIEWS:-obl eyeE eyeW closeW}; do case $v in
 oblN) run CAM_oblique_CCOM_north_wing env LOC=${OLOC:--38.0,82.0,170.0} TGT=${OTGT:--2.0,30.0,141.0} LENS=${OLENS:-28} TREE_HIDE_SEG_M=6 ;;
 closeN) run CAM_closeup_CCOM_north_wing_walltop env LOC=${CLOC:--9.0,54.0,140.0} TGT=${CTGT:--5.0,40.0,145.5} LENS=${CLENS:-30} TREE_HIDE_SEG_M=4 ;;
 obl) run CAM_oblique_CCOM_east_lawn env LOC=${OLOC:-85.0,15.0,172.0} TGT=${OTGT:-12.0,15.0,137.0} LENS=${OLENS:-28} TREE_HIDE_SEG_M=6 ;;
 eyeE) run CAM_eye_CCOM_east_lounge_glazing env LOC=${ELOC:-36.5,-19.0,136.3} TGT=${ETGT:-23.6,-22.2,137.9} LENS=${ELENS:-28} TREE_HIDE_SEG_M=4 ;;
 closeW) run CAM_closeup_CCOM_east_window_spandrel env LOC=${CLOC:-31.5,-22.6,136.4} TGT=${CTGT:-24.2,-21.8,138.6} LENS=${CLENS:-24} TREE_HIDE_SEG_M=3 ;;
 eyeN) run CAM_eye_CCOM_north_lawn env LOC=${NLOC:--12.0,58.0,139.1} TGT=${NTGT:-5.0,20.0,138.5} LENS=${NLENS:-24} TREE_HIDE_SEG_M=4 ;;
 eyeW) run CAM_eye_CCOM_lounge_west_lawn env LOC=${WLOC:--40.0,10.0,139.2} TGT=${WTGT:-0.0,12.0,140.0} LENS=${WLENS:-24} TREE_HIDE_SEG_M=4 ;;
 closeC) run CAM_closeup_CCOM_south_corridor_floor env LOC=${CLOC:-12.5,-21.9,137.2} TGT=${CTGT:--10,-16.6,136.8} LENS=${CLENS:-20} TREE_HIDE_SEG_M=3 ;;
 closeS1) run CAM_closeup_CCOM_SOUTH1_west_corner env LOC=${SLOC:--12.62,-13.16,139.0} TGT=${STGT:--20.72,-11.79,138.3} LENS=${SLENS:-20} TREE_HIDE_SEG_M=3 ;;
 close) run CAM_closeup_CCOM_east_strip_grass env LOC=${CLOC:-43.0,12.0,135.4} TGT=${CTGT:-38.0,22.0,134.7} LENS=${CLENS:-35} TREE_HIDE_SEG_M=3 ;;
 eyeLH) run CAM_eye_LifeHall_east_wing_top env LOC=${LLOC:-60.0,40.0,136.5} TGT=${LTGT:-42.0,17.0,141.5} LENS=${LLENS:-24} TREE_HIDE_SEG_M=5 ;;
 closeLH) run CAM_closeup_LifeHall_walltop_eave env LOC=${CLOC:-47.0,4.0,141.5} TGT=${CTGT:-38.6,11.5,144.6} LENS=${CLENS:-30} TREE_HIDE_SEG_M=4 ;;
 eyeMH) run CAM_eye_Morehead_west_walltop env LOC=${MLOC:--55.0,-44.0,137.1} TGT=${MTGT:--35.0,-38.0,141.5} LENS=${MLENS:-24} TREE_HIDE_SEG_M=5 ;;
 eyeLHS) run CAM_eye_LifeHall_SCM_junction env LOC=${JLOC:-47.0,-3.0,141.0} TGT=${JTGT:-35.0,6.0,144.0} LENS=${JLENS:-24} TREE_HIDE_SEG_M=5 ;;
 closeF) run CAM_closeup_CCOM_west_forecourt_herringbone env LOC=${FLOC:--31.0,5.0,138.9} TGT=${FTGT:--20.0,13.0,139.6} LENS=${FLENS:-24} TREE_HIDE_SEG_M=3 ;;
 closeT) run CAM_closeup_CCOM_tower_mulch_bed env LOC=${TLOC:--29.0,9.5,138.9} TGT=${TTGT:--19.5,19.5,140.2} LENS=${TLENS:-24} TREE_HIDE_SEG_M=3 ;;
 closeR) run CAM_closeup_SCM_flat_roof_membrane env LOC=${RLOC:-24.0,38.0,153.5} TGT=${RTGT:-6.0,18.0,145.0} LENS=${RLENS:-28} TREE_HIDE_SEG_M=3 ;;
esac; done
echo DONE_EI_RENDERS; ls -la $O/${T}_*_ei.jpg
