#!/bin/bash
# Session nc WIPs (main, studio safety cables + DMX run + floor gaffer tape + clearer south glass)
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; PY=north/scripts/render_wip_20261020cw.py
O=${OUTDIR:-/workspace/nj-scenes/montclair-state/renders/wip}; T=${1:-$(date +%Y%m%d-%H%M)}; S=${SPP:-40}
run() { free -m | awk '/^Mem:/{print "avail",$7}'; env SPP=$S PCT=${PCT:-100} OUT=$O/${T}_$1_nc.jpg CAM=$1 "${@:2}" $B -b ${BLEND:-montclair_state.blend} --python $PY 2>&1 | grep -E "RENDERED|Error"; }
v() { case $1 in
 obl) run aerial_ccom_newsroom_studio_from_southwest env LOC=-64.6,-9.9,165 TGT=-17.3,-1.9,141 LENS=32 TREE_HIDE_SEG_M=6 ;;
 eyeNW) run eye_ccom_newsroom_bay_from_northwest env LOC=-33.9,22.7,138.6 TGT=-21.7,-2.9,141.5 LENS=26 TREE_HIDE_SEG_M=4 ;;
 eyeSW) run eye_ccom_newsroom_bay_from_southwest env LOC=-46.5,-14.5,138.6 TGT=-21.5,-1.0,141.5 LENS=28 TREE_HIDE_SEG_M=4 ;;
 tray) run closeup_ccom_newsroom_grid_spot_cable_drops env LOC=-18.30,-1.69,139.20 TGT=-14.09,-10.96,143.50 LENS=22 ;;
 drop) run closeup_ccom_newsroom_grid_connector_strip_cable_drop env LOC=-22.33,-10.59,144.7 TGT=-20.78,-9.52,145.6 LENS=30 ;;
 drop2) run closeup_ccom_newsroom_grid_spot_cables_rear_bar env LOC=-16.76,-8.87,144.5 TGT=-15.93,-10.71,145.7 LENS=30 ;;
 lav) run closeup_ccom_newsroom_anchor_lav_mics_ifb env LOC=-17.70,-11.35,138.80 TGT=-17.70,-12.62,138.45 LENS=32 ;;
 safety) run closeup_ccom_newsroom_grid_spot_safety_cables_dmx env LOC=-20.25,-9.55,144.85 TGT=-20.95,-10.4,145.47 LENS=35 ;;
 safety2) run closeup_ccom_newsroom_grid_spot_safety_cable_side env LOC=-20.35,-10.95,145.30 TGT=-20.95,-10.40,145.45 LENS=40 ;;
 tape) run closeup_ccom_newsroom_floor_gaffer_tape_spike_marks env LOC=-15.7,-6.6,139.0 TGT=-17.0,-8.9,137.45 LENS=22 ;;
 ccm) run closeup_ccm_office_glass_from_inside env LOC=-6.74,-0.10,143.56 TGT=-8.44,3.66,142.76 LENS=18 ;;
 backrooms) run eye_ccom_newsroom_back_rooms_ccm_office_from_studio_floor env LOC=-18.92,0.0,139.0 TGT=-8.69,1.82,143.2 LENS=24 ;;
 cS) run closeup_ccom_gable_south_corner_rake_tip env LOC=-29.9,4.0,145.2 TGT=-21.5,8.1,147.2 LENS=40 TREE_HIDE_SEG_M=4 ;;
 cSide) run closeup_ccom_gable_south_corner_from_south env LOC=-25.62,2.52,147.3 TGT=-19.73,7.79,147.6 LENS=35 TREE_HIDE_SEG_M=4 ;;
esac; }
for x in ${ONLY:-obl eyeNW eyeSW tray}; do v $x; done; ls $O/${T}_*_nc.jpg
