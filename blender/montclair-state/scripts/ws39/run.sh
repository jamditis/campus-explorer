#!/bin/bash
cd /workspace/nj-scenes/montclair-state
for i in $(seq 1 120); do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ $a -gt 5000 ] && break; sleep 5; done
echo "start avail=$a $(date)"
cp montclair_state.blend montclair_state_pre_20261110ws39.blend
SAVE=1 WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws39/fix.py 2>&1 | grep -E "W39|rror|Traceback|line [0-9]|WATCHDOG"
sha256sum montclair_state.blend
for i in $(seq 1 120); do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ $a -gt 6500 ] && break; sleep 5; done
echo "render avail=$a $(date)"
SX=-175 SY=-112 CULL=-250,-150,-150,-60 OUT_TAG=GOLDEN_ws39_goldenhour CAMS="WS35_CAM_oblique_Kasser_Cole_frontage_from_SW=oblique_Kasser_Cole_frontage_from_SW,WS35_CAM_eye_Kasser_steps_from_CollegeAve_SW=eye_Kasser_steps_from_CollegeAve_SW_AFTER_foot_landing,WS35_CAM_eye_RedHawk_statue_match4_from_W=eye_RedHawk_statue_from_CollegeAve_wings_broad,WS35_CAM_closeup_RedHawk_statue=closeup_RedHawk_statue_pass4" WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws35/render35.py 2>&1 | grep -E "WROTE|rror:|WATCHDOG"
echo done $(date)
