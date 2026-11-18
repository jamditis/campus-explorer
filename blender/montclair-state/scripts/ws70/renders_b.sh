#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; C="-360,-150,-150,60"
JOBS=(
"wip|WS67_CAM_oblique_CollegeAve_W_to_RHD=oblique_RHD_CollegeAve_W_berms"
"wip|WS67_CAM_eye_CollegeAve_E_from_RHD_entrance=eye_CollegeAve_E_gap_strip_berms"
"wip|WS68_CAM_eye_RHD_cogen_lawn_from_S=eye_RHD_cogen_lawn_from_S"
"wip|WS69_CAM_closeup_gap_strip_curbs=closeup_gap_strip_lawn_berms")
for J in "${JOBS[@]}"; do
  IFS='|' read d cam <<< "$J"
  for try in 1 2 3; do
    a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) avail $a render $cam try $try"
    [ "$a" -lt 5800 ] && { sleep 45; continue; }
    out=$(DIR=$d CULL=$C TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=GOLDEN_ws70b_goldenhour CAMS="$cam" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws70/render70.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && break; sleep 20
  done
done
echo "$(date +%T) done"
