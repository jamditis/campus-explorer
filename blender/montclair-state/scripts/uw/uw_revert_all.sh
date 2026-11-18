#!/bin/bash
# Undo session uw polish, then restore uv Freeman overlays exactly.
# Run BEFORE uv_revert_all.sh (day-10 chain: uw → uv → uc → ub).
set -e
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
# 1) strip uw tags / lettering restore (partial)
REVERT=1 SAVE=0 $B -b "$F" --python scripts/uw/uw_polish.py 2>&1 | grep -E "UW |SAVED|Error|Traceback|REVERT" || true
# 2) full uv revert + re-apply to restore pre-uw mesh state
REVERT=1 SAVE=0 $B -b "$F" --python scripts/uv/uv_main.py 2>&1 | grep -E "UV |SAVED|Error|Traceback|REVERT" || true
SAVE=1 $B -b "$F" --python scripts/uv/uv_main.py 2>&1 | grep -E "UV |SAVED|Error|Traceback|OBJECTS" || true
echo "UW REVERT_ALL done (uv overlays restored)"
