#!/bin/bash
# Undo session vm. Run BEFORE vl_revert_all.sh (day-10 chain: vm → vl → vk → vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vm/vm_main.py 2>&1 | grep -E "VM |SAVED|Error|Traceback|REVERT" || true
echo "VM REVERT_ALL done (vm_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI/VJ/VK shadow/cream/mortar + VJ/VK/VL ibay + VL cream/shadow/mortar + VC/SE BP stashes restored)"
