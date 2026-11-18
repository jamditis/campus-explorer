#!/bin/bash
cd /workspace/nj-scenes/montclair-state
gate(){ while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" \> "${GIVEUP:-0000}" ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 6000 ] && break; sleep 5; done; echo "$(date +%T) $1 START $a"; }
gate BUILD
cp montclair_state.blend montclair_state_pre_${BK:?set BK e.g. 20261113ws107}.blend && sha256sum montclair_state_pre_${BK}.blend | cut -c1-12
SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws105/build105.py 2>&1 | grep -E "B105|CH |rror|Trace|WATCH"
sha256sum montclair_state.blend | cut -c1-12 > scripts/ws106/sha_after_build.txt; cat scripts/ws106/sha_after_build.txt
sleep 3; gate CURB
SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws106/curbback106.py 2>&1 | grep -E "C106|rror|Trace|WATCH"
sha256sum montclair_state.blend | cut -c1-12 > scripts/ws106/sha_after_curb.txt; cat scripts/ws106/sha_after_curb.txt
sleep 3; gate CUT
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws105/cut105.py 2>&1 | grep -E "CUT|rror|Trace|WATCH"
[ -f scripts/ws105/render_cut105.blend ] || { echo "NO CUT"; echo END; exit 1; }
sleep 3; echo "$(date +%T) RENDER START $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CULL=-420,-60,-420,-20 SAMP=16 PCT=55 OUT_TAG=${TAG:-wsNEXT} CAMS=WS105_CAM_oblique_W_bank_from_E=oblique_W_bank_Chapin,WS105_CAM_eye_W_bank_from_walk_N=eye_W_bank_from_walk_N,WS105_CAM_eye_W_bank_from_lower_walkway_S=eye_W_bank_from_lower_walkway_S,WS105_CAM_closeup_stair_B_from_walk=closeup_stair_B WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b scripts/ws105/render_cut105.blend --python scripts/ws105/render105.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"
echo "$(date +%T) DONE"; echo END
