#!/bin/bash
# og WIPs: exterior Schmitt cams via the od render chain (no cutaway names -> no interior hides). One Blender at a time.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=$1; O=renders/wip
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=OG_CAM_oblique_schmitt_from_SE OUT=$O/${T}_CAM_og.jpg RES=80 SPP=24 $B -b montclair_state.blend --python scripts/od/od_render.py > data/og/r_aerial.log 2>&1
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=${EYECAMS:-OG_CAM_eye_schmitt_ESE_north_lower_storey,OG_CAM_eye_schmitt_WNW_long_facade,OG_CAM_closeup_schmitt_E_entrance_door} OUT=$O/${T}_CAM_og.jpg RES=80 SPP=24 $B -b montclair_state.blend --python scripts/od/od_render.py > data/og/r_eye.log 2>&1
grep -h RENDERED data/og/r_*.log; echo RENDER_DONE
