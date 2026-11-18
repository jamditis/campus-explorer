#!/bin/bash
# Undo session vn. Run BEFORE vm_revert_all.sh (day-10 chain: vn → vm → vl → vk → vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vn/vn_main.py 2>&1 | grep -E "VN |SAVED|Error|Traceback|REVERT" || true
echo "VN REVERT_ALL done (vn_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI/VJ/VK/VL/VM shadow/cream/mortar + VJ/VK/VL/VM ibay + VC/SE BP stashes restored)"
