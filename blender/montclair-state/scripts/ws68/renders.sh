#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; C="-360,-150,-150,60"
JOBS=(
"wip|WS67_CAM_eye_CollegeAve_E_from_RHD_entrance=eye_CollegeAve_E_crosswalk_seated"
"wip|WS68_CAM_eye_RHD_cogen_lawn_from_S=eye_RHD_cogen_lawn_from_S"
"wip|WS68_CAM_closeup_crosswalk_RHD_SE=closeup_crosswalk_on_road_RHD_SE")
for J in "${JOBS[@]}"; do
  IFS='|' read d cam <<< "$J"
  for try in 1 2 3; do
    a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) avail $a render $cam try $try"
    [ "$a" -lt 5800 ] && { sleep 60; continue; }
    out=$(DIR=$d CULL=$C TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=GOLDEN_ws68c_goldenhour CAMS="$cam" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws68/render68.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && break; sleep 30
  done
done
echo "$(date +%T) done"
