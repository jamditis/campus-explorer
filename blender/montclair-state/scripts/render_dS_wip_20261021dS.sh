#!/bin/bash
# Session dS WIPs (approach of render_dR_wip_20261021dR.sh, _dS suffix; new CCOM-area views for the CCOM building day) (Oct 21 2026; all FROM MAIN).
# dS note: view eyeE (east strip) put the camera inside a tree at both tested spots -> not used for the finals; finals = obl eyeW eyeN close.
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-24}
run() { free -m | head -2; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_dS.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|SOFT|VIEW|hid trees|Error"; }
for v in ${VIEWS:-obl eyeW eyeN close}; do case $v in
 obl) run CAM_oblique_CCOM_east_lawn env LOC=${OLOC:-85.0,15.0,172.0} TGT=${OTGT:-12.0,15.0,137.0} LENS=${OLENS:-28} TREE_HIDE_SEG_M=6 ;;
 eyeE) run CAM_eye_CCOM_east_strip env LOC=${ELOC:-46.0,4.0,136.25} TGT=${ETGT:-38.0,32.0,136.0} LENS=${ELENS:-24} TREE_HIDE_SEG_M=4 ;;
 eyeN) run CAM_eye_CCOM_north_lawn env LOC=${NLOC:--12.0,58.0,139.1} TGT=${NTGT:-5.0,20.0,138.5} LENS=${NLENS:-24} TREE_HIDE_SEG_M=4 ;;
 eyeW) run CAM_eye_CCOM_lounge_west_lawn env LOC=${WLOC:--40.0,10.0,139.2} TGT=${WTGT:-0.0,12.0,140.0} LENS=${WLENS:-24} TREE_HIDE_SEG_M=4 ;;
 close) run CAM_closeup_CCOM_east_strip_grass env LOC=${CLOC:-43.0,12.0,135.4} TGT=${CTGT:-38.0,22.0,134.7} LENS=${CLENS:-35} TREE_HIDE_SEG_M=3 ;;
esac; done
echo DONE_DS_RENDERS; ls -la $O/${T}_*_dS.jpg
