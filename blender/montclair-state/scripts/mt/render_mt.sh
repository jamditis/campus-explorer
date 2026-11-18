#!/bin/bash
# Session mt WIPs (main, CCOM tower sign)
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-10}
run() { env SPP=$S PCT=${PCT:-50} OUT=$O/${T}_$1_mt.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|Error"; }
v() { case $1 in
 obl) run aerial_ccom_tower_sign_from_northwest env LOC=-62,48,172 TGT=-16,20,146 LENS=32 TREE_HIDE_SEG_M=6 ;;
 eyeW) run eye_ccom_tower_sign_entrance_from_west env LOC=-44,23,138.8 TGT=-17,20.5,147 LENS=26 TREE_HIDE_SEG_M=4 ;;
 eyeS) run eye_ccom_tower_sign_from_southwest env LOC=-38,-6,138.8 TGT=-16,20,147 LENS=26 TREE_HIDE_SEG_M=4 ;;
 gable) run closeup_ccom_entrance_gable_medallion_and_tower_sign env LOC=-35,14,141.5 TGT=-19.5,15.5,148 LENS=30 TREE_HIDE_SEG_M=4 ;;
 close) run closeup_ccom_tower_sign_lettering env LOC=-30,24,146 TGT=-18,21.2,149.3 LENS=40 TREE_HIDE_SEG_M=4 ;;
esac; }
if [ -n "$ONLY" ]; then for x in $ONLY; do v $x; done; else v obl; v eyeW; v eyeS; v close; fi; ls $O/${T}_*_mt.jpg
