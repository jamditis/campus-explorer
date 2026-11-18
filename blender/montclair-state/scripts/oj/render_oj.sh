#!/bin/bash
# oj WIPs via od_render chain + OIDN (same as oi). One Blender at a time.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=$(date +%Y%m%d-%H%M); O=${ODIR:-renders/wip}
F=${FILE:-montclair_state.blend}
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=${CAMS:-OG_CAM_oblique_schmitt_from_SE,OI_CAM_eye_schmitt_pavilion_front,OJ_CAM_eye_schmitt_pavilion_from_NNE,OJ_CAM_closeup_schmitt_pavilion_side_windows_landing}
CAMS=$CAMS EXR=1 OUT=$O/${T}_CAM_oj.jpg RES=${RES:-80} SPP=${SPP:-40} $B -b $F --python scripts/od/od_render.py > data/oj/r_$T.log 2>&1
free -m | awk '/Mem:/{print "avail",$7}'
for e in $O/${T}_*_oj.exr; do [ -f "$e" ] || continue; j=${e%.exr}.jpg; $B -b --factory-startup --python scripts/denoise_exr.py -- $e $j AgX "AgX - Base Contrast" -1.0 1024 576 > /dev/null 2>&1; ls -la $j; rm -f $e; done
ls -la $O/${T}_*_oj.jpg
echo RENDER_DONE $T
