#!/bin/bash
# Undo session vj. Run BEFORE vi_revert_all.sh (day-10 chain: vj → vi → vh → vg → vf → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vj/vj_main.py 2>&1 | grep -E "VJ |SAVED|Error|Traceback|REVERT" || true
echo "VJ REVERT_ALL done (vj_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VI shadow/cream/mortar + SE BP stashes restored)"
