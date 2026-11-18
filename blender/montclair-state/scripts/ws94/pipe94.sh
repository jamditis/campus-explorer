#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" -ge 1712 ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 6000 ] && break; sleep 10; done
echo "$(date +%T) START $a"
cp montclair_state.blend montclair_state_pre_20261112ws94b.blend
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws94/main_seam94.py 2>&1 | grep -E "P94S|rror|Trace|WATCH"
sha256sum montclair_state.blend > scripts/ws94/sha_after_b.txt
echo "$(date +%T) APPLIED"
a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
if [ "$a" -gt 6000 ]; then OUT_TAG=ws94 bash scripts/ws91/rr.sh "WS79_CAM_closeup_island_E_end_patch=closeup_island_E_end_seams_seated_final_ws94,WS79_CAM_oblique_lots_E=oblique_lots_E_final_ws94,WS78_CAM_eye_lot_from_E=eye_lot_island_from_E_final_ws94,WS78_CAM_eye_lot_from_W=eye_lots_island_from_W_seams_seated_final_ws94"; else echo "NO RENDER avail $a"; fi
echo END
