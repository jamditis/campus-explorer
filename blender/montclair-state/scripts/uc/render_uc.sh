#!/bin/bash
set -e
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
TS=$(date +%Y%m%d-%H%M)
WIP=renders/wip
mkdir -p "$WIP"
free -m | head -2
# Serial renders; abort if available < 1500
avail=$(free -m | awk '/Mem:/{print $7}')
if [ "$avail" -lt 1500 ]; then echo "LOW MEM $avail"; exit 1; fi

cams=(
  "UC_CAM_oblique_Finley_area_from_SW"
  "UC_CAM_eye_Finley_from_S"
  "UC_CAM_eye_Finley_from_E"
  "UC_CAM_closeup_Finley_wall_top"
)
tags=(oblique_Finley_area_from_SW eye_Finley_from_S eye_Finley_from_E closeup_Finley_wall_top)

for i in 0 1 2 3; do
  cam=${cams[$i]}
  tag=${tags[$i]}
  out="$WIP/${TS}_${cam}_uc.jpg"
  echo "=== $(date) $cam avail=$(free -m | awk '/Mem:/{print $7}') ==="
  avail=$(free -m | awk '/Mem:/{print $7}')
  if [ "$avail" -lt 1500 ]; then echo "LOW MEM abort"; exit 1; fi
  CAM="$cam" OUT="$out" SPP=36 RES=1280 \
    $B -b montclair_state.blend --python scripts/uc/uc_render_one.py 2>&1 \
    | grep -E 'RENDER|DONE|Error|Traceback|Failed'
  ls -la "$out" 2>/dev/null || ls -la "${out}.jpg" 2>/dev/null || ls -la renders/wip/${TS}_*uc* 2>/dev/null | tail -5
done
echo "ALL DONE TS=$TS"
ls -la renders/wip/${TS}_*_uc.jpg
