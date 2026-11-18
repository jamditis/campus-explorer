#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
for cam in WS67_CAM_closeup_CollegeAve_gap_bridge=closeup_CollegeAve_gap_from_W_bridged WS67_CAM_eye_CollegeAve_W_from_Kasser_steps=eye_CollegeAve_W_from_Kasser_steps WS67_CAM_eye_CollegeAve_E_from_RHD_entrance=eye_CollegeAve_E_from_RHD_entrance; do
 for try in 1 2; do
  echo "$(date +%T) avail $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) $cam try $try"
  out=$(DIR=wip CULL="-330,-170,-130,40" TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=GOLDEN_ws67b_lite_goldenhour CAMS="$cam" WD_MIN=1100 bash scripts/ws33/wd.sh $B -b --factory-startup --python scripts/ws67/lite_render67.py 2>&1 | grep -E "WROTE|WATCHDOG|rror|LR kept"); echo "$out"
  echo "$out" | grep -q WROTE && break; sleep 20
 done
done; echo "$(date +%T) done"
