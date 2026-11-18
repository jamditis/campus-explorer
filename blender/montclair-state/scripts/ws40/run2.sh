#!/bin/bash
cd /workspace/nj-scenes/montclair-state
cp montclair_state.blend montclair_state_pre_20261110ws40b.blend
SAVE=1 WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws40/fix2.py 2>&1 | grep -E "F40|rror|Traceback|WATCHDOG" | cut -c1-500
sha256sum montclair_state.blend
SX=-175 SY=-112 CULL=-250,-150,-150,-60 OUT_TAG=GOLDEN_ws40_goldenhour CAMS="WS35_CAM_oblique_Kasser_Cole_frontage_from_SW=oblique_Kasser_Cole_frontage_from_SW_b,WS40_CAM_eye_steps_from_CollegeAve_W=eye_Kasser_steps_from_CollegeAve_W_sidewalk_b,WS40_CAM_eye_down_steps_from_deck_E=eye_down_steps_to_CollegeAve_from_deck_E_b,WS40_CAM_closeup_steps_foot_sidewalk=closeup_steps_foot_sidewalk_fascia_b" WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws40/render40.py 2>&1 | grep -E "WROTE|rror:|WATCHDOG"
echo done $(date)
