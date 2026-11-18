#!/bin/bash
# Session dg WIPs (Oct 20 2026; all FROM MAIN; PY = north/scripts/render_wip_20261020cw.py, soft light read-only; one Blender at a time).
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-24}
run() { free -m | head -2; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_dg.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|SOFT|VIEW|hid trees|Error"; }
for v in ${VIEWS:-obl lawn mh let}; do case $v in
 obl) run CAM_oblique_sprague_roof_letters env LOC=${OLOC:-5.0,20.0,175.0} TGT=${OTGT:--52.0,50.0,142.0} LENS=${OLENS:-35} TREE_HIDE_SEG_M=6 ;;
 lawn) run CAM_eye_sprague_lawn_letters env LOC=${LLOC:--20.0,18.0,139.3} TGT=${LTGT:--52.0,40.0,142.5} LENS=${LLENS:-24} TREE_HIDE_SEG_M=4 ;;
 mh) run CAM_eye_Morehead_west_entrance env LOC=${MLOC:--58.0,-36.0,136.4} TGT=${MTGT:--37.0,-42.3,140.2} LENS=${MLENS:-28} TREE_HIDE_SEG_M=4 ;;
 let) run CAM_closeup_sprague_library_letters_photo09 env LOC=${CLOC:--38.98,25.28,139.6} TGT=${CTGT:--47.79,31.47,141.3} LENS=${CLENS:-32} TREE_HIDE_SEG_M=3 ;;
esac; done
echo DONE_DG_RENDERS; ls -la $O/${T}_*_dg.jpg
