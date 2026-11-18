#!/bin/bash
# Undo session vl. Run BEFORE vk_revert_all.sh (day-10 chain: vl → vk → vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vl/vl_main.py 2>&1 | grep -E "VL |SAVED|Error|Traceback|REVERT" || true
echo "VL REVERT_ALL done (vl_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI/VJ/VK shadow/cream/mortar + VJ/VK ibay + VC/SE BP stashes restored)"
