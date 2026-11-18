#!/bin/bash
# oe WIPs: od cameras, od/oc render chain (oe changed only one material); aerial batch then eye+closeup batch, one Blender at a time.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=$1; O=renders/wip
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=OD_CAM_aerial_cutaway_atrium_stair_to_east_from_W OUT=$O/${T}_CAM_oe.jpg RES=80 SPP=24 $B -b montclair_state.blend --python scripts/od/od_render.py > data/oe/r_aerial.log 2>&1
free -m | awk '/Mem:/{print "avail",$7}'
CAMS=OD_CAM_eye_atrium_stair_guard_looking_NE,OD_CAM_eye_1F_east_end_from_NE_looking_SW,OE_CAM_closeup_atrium_stair_wall_panels_handrail OUT=$O/${T}_CAM_oe.jpg RES=80 SPP=24 $B -b montclair_state.blend --python scripts/od/od_render.py > data/oe/r_eye.log 2>&1
grep -h RENDERED data/oe/r_*.log; echo RENDER_DONE
