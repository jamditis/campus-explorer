#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=$(date +%Y%m%d-%H%M); O=${ODIR:-renders/wip}
F=${FILE:-montclair_state.blend}
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=${CAMS:-OO_CAM_oblique_redraped_walks_NNE_of_schmitt,OP_CAM_eye_redraped_road_E_campus_edge,OQ_CAM_eye_calcia_skirt_windows,OQ_CAM_closeup_CCIS_skirt_windows}
CAMS=$CAMS EXR=1 OUT=$O/${T}_CAM_oq.jpg RES=${RES:-80} SPP=${SPP:-40} $B -b $F --python scripts/od/od_render.py > data/oq/r_$T.log 2>&1
free -m | awk '/Mem:/{print "avail",$7}'
for e in $O/${T}_*_oq.exr; do [ -f "$e" ] || continue; j=${e%.exr}.jpg; $B -b --factory-startup --python scripts/denoise_exr.py -- $e $j AgX "AgX - Base Contrast" -1.0 1024 576 > /dev/null 2>&1; ls -la $j; rm -f $e; done
ls -la $O/${T}_*_oq.jpg
echo RENDER_DONE $T
