#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=$(date +%Y%m%d-%H%M); O=${ODIR:-renders/wip}
F=${FILE:-montclair_state.blend}
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=${CAMS:-PE_CAM_oblique_dickson_from_SW,PE_CAM_eye_dickson_west,PV_CAM_eye_dickson_north,PZ_CAM_closeup_dickson_wing_nw_corner}
CAMS=$CAMS EXR=1 OUT=$O/${T}_CAM_pz.jpg RES=${RES:-80} SPP=${SPP:-40} $B -b $F --python scripts/pz/pw_render_lowmem.py > data/pz/r_$T.log 2>&1
free -m | awk '/Mem:/{print "avail",$7}'
for e in $O/${T}_*_pz.exr; do [ -f "$e" ] || continue; j=${e%.exr}.jpg; $B -b --factory-startup --python scripts/denoise_exr.py -- $e $j AgX "AgX - Base Contrast" -1.0 1024 576 > /dev/null 2>&1; ls -la $j; rm -f $e; done
ls -la $O/${T}_*_pz.jpg
echo RENDER_DONE $T
