#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" \> "0340" ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 6300 ] && break; sleep 5; done
echo "$(date +%T) CUT START $a"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws104/cut104.py 2>&1 | grep -E "CUT|rror|Trace|WATCH"
[ -f scripts/ws104/render_cut104.blend ] || { echo "NO CUT"; echo END; exit 1; }
sleep 3; echo "$(date +%T) RENDER START $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CULL=-420,-60,-420,-20 SAMP=16 PCT=55 OUT_TAG=ws104 CAMS=WS104_CAM_closeup_table_N_edge_from_NW=closeup_table_N_edge_joint_v2,WS102_CAM_eye_CollegeAve_S_from_N=eye_CollegeAve_S_from_N_v2 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b scripts/ws104/render_cut104.blend --python scripts/ws104/render104.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"
echo "$(date +%T) DONE"; echo END
