#!/bin/bash
# Undo session vc. Run BEFORE vb_revert_all.sh (day-10 chain: vc → vb → va → uy → uw → uv → uc → ub).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vc/vc_main.py 2>&1 | grep -E "VC |SAVED|Error|Traceback|REVERT" || true
echo "VC REVERT_ALL done (vc_obj/mats removed; prior material slots restored)"
