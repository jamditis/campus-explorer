#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; C="-330,-170,-130,40"
JOBS=("montclair_state_pre_20261111ws67.blend|test|BEFORE_ws67|WS67_CAM_eye_CollegeAve_W_from_Kasser_steps=eye_CollegeAve_W_from_Kasser_steps_before"
"montclair_state_pre_20261111ws67.blend|test|BEFORE_ws67|WS67_CAM_closeup_CollegeAve_gap_bridge=closeup_CollegeAve_gap_before"
"montclair_state.blend|wip|GOLDEN_ws67_goldenhour|WS67_CAM_oblique_CollegeAve_W_to_RHD=oblique_CollegeAve_W_regraded_to_RHD"
"montclair_state.blend|wip|GOLDEN_ws67_goldenhour|WS67_CAM_eye_CollegeAve_W_from_Kasser_steps=eye_CollegeAve_W_from_Kasser_steps"
"montclair_state.blend|wip|GOLDEN_ws67_goldenhour|WS67_CAM_eye_CollegeAve_E_from_RHD_entrance=eye_CollegeAve_E_from_RHD_entrance"
"montclair_state.blend|wip|GOLDEN_ws67_goldenhour|WS67_CAM_closeup_CollegeAve_gap_bridge=closeup_CollegeAve_gap_bridged")
for J in "${JOBS[@]}"; do
  IFS='|' read f d tag cam <<< "$J"
  for try in 1 2 3; do
    a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) avail $a render $cam ($f) try $try"
    [ "$a" -lt 5800 ] && { sleep 60; continue; }
    out=$(DIR=$d CULL=$C TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=$tag CAMS="$cam" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b $f --python scripts/ws67/render67.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && break; sleep 30
  done
done
echo "$(date +%T) done"
