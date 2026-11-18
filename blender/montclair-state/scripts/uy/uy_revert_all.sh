#!/bin/bash
# Undo session uy. Run BEFORE uw_revert_all.sh (day-10 chain: uy → uw → uv → uc → ub).
set -e
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uy/uy_main.py 2>&1 | grep -E "UY |SAVED|Error|Traceback|REVERT" || true
echo "UY REVERT_ALL done (uy_obj/mats removed; prior orange bay unhidden if uy_hid_prev)"
