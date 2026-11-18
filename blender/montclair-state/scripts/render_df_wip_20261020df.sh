#!/bin/bash
# Session df WIPs (Oct 20 2026; all FROM MAIN; PY = north/scripts/render_wip_20261020cw.py, soft light read-only; one Blender at a time).
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-24}
run() { free -m | head -2; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_df.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|SOFT|VIEW|hid trees|Error"; }
for v in ${VIEWS:-obl lawn p08 wing}; do case $v in
 obl) run CAM_oblique_sprague_wing_de env LOC=${OLOC:-5.0,20.0,175.0} TGT=${OTGT:--52.0,50.0,142.0} LENS=${OLENS:-35} TREE_HIDE_SEG_M=6 ;;
 lawn) run CAM_eye_sprague_lawn_wing_de env LOC=${LLOC:--20.0,18.0,139.3} TGT=${LTGT:--52.0,46.0,143.0} LENS=${LLENS:-24} TREE_HIDE_SEG_M=4 ;;
 p08) run CAM_eye_cafe_diem_photo08_wing env LOC=${PLOC:--22.0,36.0,139.4} TGT=${PTGT:--54.0,52.0,143.6} LENS=${PLENS:-32} TREE_HIDE_SEG_M=4 ;;
 wing) run CAM_closeup_sprague_wing_screens env LOC=${WLOC:--39.0,42.0,147.5} TGT=${WTGT:--55.0,46.5,144.6} LENS=${WLENS:-30} TREE_HIDE_SEG_M=3 ;;
 uh) run CAM_closeup_uh_south_impost env LOC=${ULOC:--123.75,272.0,180.5} TGT=${UTGT:--123.75,291.3,183.3} LENS=${ULENS:-55} TREE_HIDE_SEG_M=3 ;;
esac; done
echo DONE_DE_RENDERS; ls -la $O/${T}_*_df.jpg
