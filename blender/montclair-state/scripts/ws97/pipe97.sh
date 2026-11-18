#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" -ge 2010 ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 6000 ] && break; sleep 10; done
echo "$(date +%T) START $a"
sha256sum montclair_state.blend > scripts/ws97/sha_before.txt
cp montclair_state.blend montclair_state_pre_20261112ws97.blend
SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws97/apply97.py 2>&1 | grep -E "A96|rror|Trace|WATCH"
sha256sum montclair_state.blend > scripts/ws97/sha_after.txt
echo "$(date +%T) APPLIED"
a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
if [ "$a" -gt 6000 ]; then OUT_TAG=ws97 bash scripts/ws91/rr.sh "WS79_CAM_closeup_island_E_end_patch=closeup_lot_E_edge_lawn_seated_ws97,WS79_CAM_oblique_lots_E=oblique_lots_E_ws97,WS78_CAM_eye_lot_from_E=eye_lot_island_from_E_ws97,WS78_CAM_eye_lot_from_W=eye_lots_from_W_ws97"; else echo "NO RENDER avail $a"; fi
echo END
