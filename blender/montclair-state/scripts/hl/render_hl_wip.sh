#!/bin/bash
# Session hl WIPs (main, amphitheater)
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-20}
run() { env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_hl.jpg CAM=$1 "${@:2}" $B -b montclair_state.blend --python $PY 2>&1 | grep -E "RENDERED|Error"; }
v() { case $1 in
 obl) run CAM_oblique_kasser_amphitheater_s env LOC=-150,-38,162 TGT=-172,14,136 LENS=30 TREE_HIDE_SEG_M=6 ;;
 eyeS) run CAM_eye_amphitheater_from_stage env LOC=-168,-14,134.2 TGT=-172,20,138 LENS=24 TREE_HIDE_SEG_M=4 ;;
 eyeN) run CAM_eye_amphitheater_top_row_to_kasser env LOC=-176,30,143.0 TGT=-170,-12,134 LENS=24 TREE_HIDE_SEG_M=4 ;;
 close) run CAM_closeup_amphitheater_seat_rows env LOC=-164,-1,134.6 TGT=-171,9,135.6 LENS=32 TREE_HIDE_SEG_M=3 ;;
esac; }
T=$T; (v obl; v eyeN) & (v eyeS; v close); wait; ls $O/${T}_*_hl.jpg
