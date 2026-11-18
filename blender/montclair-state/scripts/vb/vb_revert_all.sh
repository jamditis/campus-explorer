#!/bin/bash
# Undo session vb. Run BEFORE va_revert_all.sh (day-10 chain: vb → va → uy → uw → uv → uc → ub).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vb/vb_main.py 2>&1 | grep -E "VB |SAVED|Error|Traceback|REVERT" || true
echo "VB REVERT_ALL done (vb_obj/mats removed; prior material slots restored)"
