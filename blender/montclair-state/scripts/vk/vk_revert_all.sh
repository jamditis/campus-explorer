#!/bin/bash
# Undo session vk. Run BEFORE vj_revert_all.sh (day-10 chain: vk → vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vk/vk_main.py 2>&1 | grep -E "VK |SAVED|Error|Traceback|REVERT" || true
echo "VK REVERT_ALL done (vk_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI/VJ shadow/cream/mortar + VJ ibay + SE BP stashes restored)"
