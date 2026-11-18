#!/bin/bash
# Undo session vp. Run BEFORE vo_revert_all.sh (day-10 chain: vp → vo → vn → vm → vl → vk → vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vp/vp_main.py 2>&1 | grep -E "VP |SAVED|Error|Traceback|REVERT" || true
echo "VP REVERT_ALL done (vp_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI/VJ/VK/VL/VM/VN/VO shadow/cream/mortar + VJ/VK/VL/VM/VN/VO ibay + VC/SE BP stashes restored)"
