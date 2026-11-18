#!/bin/bash
# Session mx WIPs (main, CCOM NJ PBS studio: south-face windows + studio detail)
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-40}
run() { free -m | awk '/^Mem:/{print "avail",$7}'; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_mx.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|Error"; }
v() { case $1 in
 obl) run aerial_ccom_newsroom_studio_from_southwest env LOC=-64.6,-9.9,165 TGT=-17.3,-1.9,141 LENS=32 TREE_HIDE_SEG_M=6 ;;
 front) run eye_ccom_newsroom_bay_straight_on_from_west env LOC=-44.9,3.2,138.8 TGT=-21.6,-2.5,141.8 LENS=26 TREE_HIDE_SEG_M=4 ;;
 eyeNW) run eye_ccom_newsroom_bay_from_northwest env LOC=-33.9,22.7,138.6 TGT=-21.7,-2.9,141.5 LENS=26 TREE_HIDE_SEG_M=4 ;;
 close) run closeup_ccom_newsroom_set_cameras_chairs_through_glazing env LOC=-24.93,-5.22,139.10 TGT=-16.95,-10.88,138.50 LENS=30 TREE_HIDE_SEG_M=4 ;;
 inside) run interior_ccom_newsroom_set_south_windows env LOC=-18.30,-1.69,141.50 TGT=-18.32,-13.53,140.80 LENS=22 ;;
esac; }
for x in ${ONLY:-obl front eyeNW close}; do v $x; done; ls $O/${T}_*_mx.jpg
