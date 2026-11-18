#!/bin/bash
# Session nd WIPs (main; studio south glass check + floor cable tape + DMX terminators)
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-40}
run() { free -m | awk '/^Mem:/{print "avail",$7}'; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_nd.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|Error|camera"; }
v() { case $1 in
 obl) run aerial_ccom_newsroom_studio_from_southwest env LOC=-64.6,-9.9,165 TGT=-17.3,-1.9,141 LENS=32 TREE_HIDE_SEG_M=6 ;;
 eyeNW) run eye_ccom_newsroom_bay_from_northwest env LOC=-33.9,22.7,138.6 TGT=-21.7,-2.9,141.5 LENS=26 TREE_HIDE_SEG_M=4 ;;
 eyeS) run eye_ccom_newsroom_south_glass_from_south env LOC=${SLOC:--20.35,-21.67,139.3} TGT=-18.45,-13.9,140.6 LENS=${SLENS:-24} TREE_HIDE_SEG_M=4 ;;
 eyeSW) run eye_ccom_newsroom_bay_from_southwest env LOC=-46.5,-14.5,138.6 TGT=-21.5,-1.0,141.5 LENS=28 TREE_HIDE_SEG_M=4 ;;
 tape) run closeup_ccom_newsroom_floor_cable_tape_crossings env LOC=${TLOC:--12.2,-4.2,138.9} TGT=${TTGT:--13.4,-7.0,137.42} LENS=24 ;;
 term) run closeup_ccom_newsroom_grid_dmx_terminator env LOC=${XLOC:--14.0,-6.0,145.0} TGT=${XTGT:--14.0,-6.0,145.4} LENS=35 ;;
esac; }
for x in ${ONLY:-obl eyeNW eyeS tape}; do v $x; done; ls $O/${T}_*_nd.jpg
