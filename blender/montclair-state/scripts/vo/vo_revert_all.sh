#!/bin/bash
# Undo session vo. Run BEFORE vn_revert_all.sh (day-10 chain: vo → vn → vm → vl → vk → vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vo/vo_main.py 2>&1 | grep -E "VO |SAVED|Error|Traceback|REVERT" || true
echo "VO REVERT_ALL done (vo_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI/VJ/VK/VL/VM/VN shadow/cream/mortar + VJ/VK/VL/VM/VN ibay + VC/SE BP stashes restored)"
