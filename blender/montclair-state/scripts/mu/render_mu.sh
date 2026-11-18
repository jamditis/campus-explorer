#!/bin/bash
# Session mu WIPs (main, CCOM eave ends at the entrance gable)
cd /workspace/nj-scenes/montclair-state
B=../tools/blender_slot.sh; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-10}
run() { free -m | awk '/^Mem:/{print "avail",$7}'; env SPP=$S PCT=${PCT:-50} OUT=$O/${T}_$1_mu.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|Error"; }
v() { case $1 in
 obl) run aerial_ccom_entrance_gable_eave_returns_from_northwest env LOC=-62,48,172 TGT=-16,20,146 LENS=32 TREE_HIDE_SEG_M=6 ;;
 eyeW) run eye_ccom_entrance_gable_from_west env LOC=-44,23,138.8 TGT=-17,20.5,147 LENS=26 TREE_HIDE_SEG_M=4 ;;
 eyeS) run eye_ccom_entrance_gable_from_southwest env LOC=-38,-6,138.8 TGT=-16,20,147 LENS=26 TREE_HIDE_SEG_M=4 ;;
 cS) run closeup_ccom_gable_south_eave_end env LOC=-29.9,4.0,145.2 TGT=-21.5,8.1,147.2 LENS=40 TREE_HIDE_SEG_M=4 ;;
 cN) run closeup_ccom_gable_north_eave_end env LOC=-26.5,23.5,145.2 TGT=-19.7,15.5,147.2 LENS=40 TREE_HIDE_SEG_M=4 ;;
 cTopN) run closeup_ccom_gable_north_valley_from_above env LOC=-25.45,22.5,153 TGT=-17.35,13.4,148 LENS=35 TREE_HIDE_SEG_M=4 ;;
 cTop) run closeup_ccom_gable_valley_from_above env LOC=-30,4,153 TGT=-20,12,148 LENS=35 TREE_HIDE_SEG_M=4 ;;
esac; }
for x in ${ONLY:-obl eyeW eyeS cS}; do v $x; done; ls $O/${T}_*_mu.jpg
