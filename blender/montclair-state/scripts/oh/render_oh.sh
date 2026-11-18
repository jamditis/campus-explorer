#!/bin/bash
# oh WIPs: EXR + OIDN denoise (denoise_exr.py with explicit AgX / size). One Blender at a time.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=$(date +%Y%m%d-%H%M); O=renders/wip
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=${CAMS:-OG_CAM_oblique_schmitt_from_SE,OG_CAM_eye_schmitt_ESE_north_lower_storey,OH_CAM_eye_schmitt_SSW_end,OG_CAM_closeup_schmitt_E_entrance_door}
CAMS=$CAMS EXR=1 OUT=$O/${T}_CAM_oh.jpg RES=80 SPP=24 $B -b montclair_state.blend --python scripts/od/od_render.py > data/oh/r_final.log 2>&1
free -m | awk '/Mem:/{print "avail",$7}'
for e in $O/${T}_*_oh.exr; do j=${e%.exr}.jpg; $B -b --factory-startup --python scripts/denoise_exr.py -- $e $j AgX "AgX - Base Contrast" -1.0 1024 576 > /dev/null 2>&1; ls -la $j; rm -f $e; done
echo RENDER_DONE
