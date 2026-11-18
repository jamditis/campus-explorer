#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=$(date +%Y%m%d-%H%M); O=${ODIR:-renders/wip}
F=${FILE:-montclair_state.blend}
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=${CAMS:-OT_CAM_aerial_north_strip_CELS_Calcia,OR_CAM_eye_CELS_skirt_windows_base_course,OQ_CAM_eye_calcia_skirt_windows,OV_CAM_closeup_CELS_skirt_gapfill}
CAMS=$CAMS EXR=1 OUT=$O/${T}_CAM_pa.jpg RES=${RES:-80} SPP=${SPP:-40} $B -b $F --python scripts/ot/ot_render_lowmem.py > data/pa/r_$T.log 2>&1
free -m | awk '/Mem:/{print "avail",$7}'
for e in $O/${T}_*_pa.exr; do [ -f "$e" ] || continue; j=${e%.exr}.jpg; $B -b --factory-startup --python scripts/denoise_exr.py -- $e $j AgX "AgX - Base Contrast" -1.0 1024 576 > /dev/null 2>&1; ls -la $j; rm -f $e; done
ls -la $O/${T}_*_pa.jpg
echo RENDER_DONE $T
