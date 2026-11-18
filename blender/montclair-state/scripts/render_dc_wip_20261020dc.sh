#!/bin/bash
# Session dc WIPs (Oct 20 2026; all FROM MAIN; PY = north/scripts/render_wip_20261020cw.py, soft light read-only; one Blender at a time via tools/blender_slot.sh).
# Views: obl = CAM_oblique_CCOM_east_jf (saved cam), east = eye level from the EAST at the lounge glazing, p05 = Cafe Diem walk ~ Joe photo 05 (db cam), close = just outside the east lounge window.
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-24}
run() { free -m | head -2; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_dc.jpg CAM=$1 "${@:2}" $B -b montclair_state.blend --python $PY 2>&1 | grep -E "RENDERED|SOFT|VIEW|hid trees|Error"; }
for v in ${VIEWS:-obl east p05 close}; do case $v in
 obl) run CAM_oblique_CCOM_east_jf env TREE_HIDE_SEG_M=6 ;;
 east) run CAM_eye_CCOM_east_lounge_glazing_dc env LOC=${ELOC:-36.5,-19.0,136.3} TGT=${ETGT:-23.6,-22.2,137.9} LENS=${ELENS:-28} TREE_HIDE_SEG_M=4 ;;
 p05) run CAM_eye_cafe_diem_walk_photo05_main env LOC=-40.0,30.0,139.55 TGT=-47.5,62.0,140.3 LENS=24 TREE_HIDE_SEG_M=4 ;;
 close) run CAM_closeup_CCOM_east_lounge_interior_dc env LOC=${CLOC:-29.5,-23.0,136.3} TGT=${CTGT:-20.0,-20.8,137.0} LENS=${CLENS:-24} TREE_HIDE_SEG_M=3 ;;
esac; done
echo DONE_DC_RENDERS; ls -la $O/${T}_*_dc.jpg
