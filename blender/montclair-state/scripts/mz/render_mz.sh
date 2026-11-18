#!/bin/bash
# Session mz WIPs (main, CCOM NJ PBS studio detail pass 3)
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-40}
run() { free -m | awk '/^Mem:/{print "avail",$7}'; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_mz.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|Error"; }
v() { case $1 in
 obl) run aerial_ccom_newsroom_studio_from_southwest env LOC=-64.6,-9.9,165 TGT=-17.3,-1.9,141 LENS=32 TREE_HIDE_SEG_M=6 ;;
 eyeNW) run eye_ccom_newsroom_bay_from_northwest env LOC=-33.9,22.7,138.6 TGT=-21.7,-2.9,141.5 LENS=26 TREE_HIDE_SEG_M=4 ;;
 eyeSW) run eye_ccom_newsroom_bay_from_southwest env LOC=-46.5,-14.5,138.6 TGT=-21.5,-1.0,141.5 LENS=28 TREE_HIDE_SEG_M=4 ;;
 front) run eye_ccom_newsroom_bay_straight_on_from_west env LOC=-44.9,3.2,138.8 TGT=-21.6,-2.5,141.8 LENS=26 TREE_HIDE_SEG_M=4 ;;
 icl) run closeup_ccom_newsroom_interior_cameras_from_operator_side env LOC=${ILOC:--20.5,-3.1,139.4} TGT=${ITGT:--15.83,-11.76,138.3} LENS=24 ;;
 desk) run closeup_ccom_newsroom_pedestal_prompters_from_anchor_desk env LOC=${DLOC:--18.42,-12.27,139.00} TGT=${DTGT:--16.28,-7.75,138.60} LENS=${DLENS:-24} ;;
 tray) run closeup_ccom_newsroom_ceiling_cable_tray env LOC=-18.30,-1.69,139.20 TGT=-14.09,-10.96,143.50 LENS=22 ;;
 ramp) run closeup_ccom_newsroom_cable_ramp_floor_box env LOC=-16.08,-9.03,138.50 TGT=-13.69,-7.66,137.42 LENS=28 ;;
 coil) run closeup_ccom_newsroom_orange_cord_coil_tripod env LOC=-20.74,-8.30,138.40 TGT=-21.21,-6.44,137.42 LENS=26 ;;
esac; }
for x in ${ONLY:-obl eyeNW eyeSW desk}; do v $x; done; ls $O/${T}_*_mz.jpg
