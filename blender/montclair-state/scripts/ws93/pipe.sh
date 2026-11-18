#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" -ge 1610 ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 5500 ] && break; sleep 10; done
echo "$(date +%T) START $a"
sha256sum montclair_state.blend > scripts/ws93/sha_before.txt
cp montclair_state.blend montclair_state_pre_20261112ws93.blend
SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws92/apply92.py 2>&1 | grep -E "P92|rror|Trace|WATCH"
sha256sum montclair_state.blend > scripts/ws93/sha_after.txt
echo "$(date +%T) APPLIED"
a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
if [ "$a" -gt 6000 ]; then OUT_TAG=ws93 bash scripts/ws91/rr.sh "WS72_CAM_closeup_KasserS_east_from_road=closeup_KasserS_walk_curb_filler_ws93,WS90_CAM_oblique_CollegeAve_bend_from_S=oblique_CollegeAve_bend_from_S_ws93,WS89_CAM_eye_median_from_CollegeAve_E=eye_mulch_median_from_CollegeAve_E_ws93,WS78_CAM_eye_lot_from_W=eye_lots_island_from_W_ws93"; else echo "NO RENDER avail $a"; fi
echo END
