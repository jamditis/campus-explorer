#!/bin/bash
# Session dd WIPs (Oct 20 2026; all FROM MAIN; PY = north/scripts/render_wip_20261020cw.py, soft light read-only; one Blender at a time via tools/blender_slot.sh).
# obl = CAM_oblique_CCOM_east_jf (saved cam); east = dc east-lawn lounge cam; west = eye level from the WEST lawn toward the entrance (1st-floor west run);
# win4 = close-up of the new 4-pane east lounge window. LOC cams are not saved in the blend.
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-24}
run() { free -m | head -2; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_dd.jpg CAM=$1 "${@:2}" $B -b montclair_state.blend --python $PY 2>&1 | grep -E "RENDERED|SOFT|VIEW|hid trees|Error"; }
for v in ${VIEWS:-obl east west win4}; do case $v in
 obl) run CAM_oblique_CCOM_east_jf env TREE_HIDE_SEG_M=6 ;;
 east) run CAM_eye_CCOM_east_lounge_glazing_dc env LOC=36.5,-19.0,136.3 TGT=23.6,-22.2,137.9 LENS=28 TREE_HIDE_SEG_M=4 ;;
 west) run CAM_eye_CCOM_west_1f_to_entrance env LOC=${WLOC:--34.0,-12.0,137.9} TGT=${WTGT:--20.0,2.0,138.3} LENS=${WLENS:-24} TREE_HIDE_SEG_M=4 ;;
 south) run CAM_eye_CCOM_south_1f env LOC=${SLOC:--5.0,-30.0,138.0} TGT=${STGT:-6.0,-22.0,137.6} LENS=${SLENS:-24} TREE_HIDE_SEG_M=4 ;;
 p05) run CAM_eye_cafe_diem_walk_photo05_main env LOC=-40.0,30.0,139.55 TGT=-47.5,62.0,140.3 LENS=24 TREE_HIDE_SEG_M=4 ;;
 cafecol) run CAM_eye_cafe_diem_columns env LOC=${KLOC:--41.5,42.0,139.5} TGT=${KTGT:--48.5,56.0,140.0} LENS=${KLENS:-28} TREE_HIDE_SEG_M=4 ;;
 win4) run CAM_closeup_CCOM_east_window_4pane env LOC=${CLOC:-31.5,-22.6,136.4} TGT=${CTGT:-24.2,-21.8,138.4} LENS=${CLENS:-24} TREE_HIDE_SEG_M=3 ;;
esac; done
echo DONE_DD_RENDERS; ls -la $O/${T}_*_dd.jpg
