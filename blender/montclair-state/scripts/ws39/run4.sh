#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while pgrep -f scripts/ws39/run3.sh >/dev/null; do sleep 3; done
cp montclair_state.blend montclair_state_pre_20261110ws39c.blend
SAVE=1 WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws39/lawnbox.py 2>&1 | grep -E "L39|rror|Traceback|WATCHDOG"
sha256sum montclair_state.blend
SX=-175 SY=-112 CULL=-250,-150,-150,-60 OUT_TAG=GOLDEN_ws39_goldenhour CAMS="WS35_CAM_oblique_Kasser_Cole_frontage_from_SW=oblique_Kasser_Cole_frontage_from_SW_final,WS35_CAM_eye_Kasser_steps_from_CollegeAve_SW=eye_Kasser_steps_from_CollegeAve_SW_final_landing_lawn" WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws35/render35.py 2>&1 | grep -E "WROTE|rror:|WATCHDOG"
echo done $(date)
