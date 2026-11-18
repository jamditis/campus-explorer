#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=$(date +%Y%m%d-%H%M); O=${ODIR:-renders/wip}
F=${FILE:-montclair_state.blend}
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=${CAMS:-OP_CAM_oblique_redraped_roads_E_campus,OP_CAM_eye_redraped_road_E_campus_edge,OO_CAM_eye_redraped_walk_N_of_schmitt,OP_CAM_closeup_redraped_road_E_of_schmitt}
CAMS=$CAMS EXR=1 OUT=$O/${T}_CAM_op.jpg RES=${RES:-80} SPP=${SPP:-40} $B -b $F --python scripts/od/od_render.py > data/op/r_$T.log 2>&1
free -m | awk '/Mem:/{print "avail",$7}'
for e in $O/${T}_*_op.exr; do [ -f "$e" ] || continue; j=${e%.exr}.jpg; $B -b --factory-startup --python scripts/denoise_exr.py -- $e $j AgX "AgX - Base Contrast" -1.0 1024 576 > /dev/null 2>&1; ls -la $j; rm -f $e; done
ls -la $O/${T}_*_op.jpg
echo RENDER_DONE $T
