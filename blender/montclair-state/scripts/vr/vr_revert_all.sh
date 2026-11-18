#!/bin/bash
# Undo session vr. Run BEFORE vq_revert_all.sh (day-10 chain: vr → vq → vp → vo → vn → vm → vl → vk → vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vr/vr_main.py 2>&1 | grep -E "VR |SAVED|Error|Traceback|REVERT" || true
echo "VR REVERT_ALL done (vr_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI/VJ/VK/VL/VM/VN/VO/VP/VQ shadow/cream/mortar + VJ/VK/VL/VM/VN/VO/VP/VQ ibay + VC/SE BP stashes restored)"
