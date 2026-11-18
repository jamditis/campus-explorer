#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" \> "0230" ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 6300 ] && break; sleep 5; done
echo "$(date +%T) CUT START $a"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws103/cut103.py 2>&1 | grep -E "CUT|rror|Trace|WATCH"
[ -f scripts/ws103/render_cut103.blend ] || { echo "NO CUT"; echo END; exit 1; }
sleep 3; echo "$(date +%T) RENDER START $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CULL=-420,-60,-420,-20 SAMP=16 PCT=55 OUT_TAG=ws103 CAMS=WS102_CAM_closeup_plaza_bands_curb_start=closeup_plaza_W_walk_v2,WS102_CAM_eye_CollegeAve_S_from_N=eye_CollegeAve_S_from_N_v2,WS102_CAM_oblique_CollegeAve_S_from_SE=oblique_CollegeAve_S_Wwalk_v2 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b scripts/ws103/render_cut103.blend --python scripts/ws103/render103.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"
echo "$(date +%T) DONE"; echo END
