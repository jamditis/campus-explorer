#!/bin/bash
cd /workspace/nj-scenes/montclair-state
SAVE=1 WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws39/tuck2.py 2>&1 | grep -E "W39T|rror|Traceback|WATCHDOG"
sha256sum montclair_state.blend
SX=-175 SY=-112 CULL=-250,-150,-150,-60 OUT_TAG=GOLDEN_ws39_goldenhour CAMS="WS35_CAM_eye_Kasser_steps_from_CollegeAve_SW=eye_Kasser_steps_from_CollegeAve_SW_AFTER_landing_final" WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws35/render35.py 2>&1 | grep -E "WROTE|rror:|WATCHDOG"
echo done $(date)
