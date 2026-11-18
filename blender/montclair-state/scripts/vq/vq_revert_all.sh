#!/bin/bash
# Undo session vq. Run BEFORE vp_revert_all.sh (day-10 chain: vq → vp → vo → vn → vm → vl → vk → vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vq/vq_main.py 2>&1 | grep -E "VQ |SAVED|Error|Traceback|REVERT" || true
echo "VQ REVERT_ALL done (vq_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI/VJ/VK/VL/VM/VN/VO/VP shadow/cream/mortar + VJ/VK/VL/VM/VN/VO/VP ibay + VC/SE BP stashes restored)"
