#!/bin/bash
# Undo session vd. Run BEFORE vc_revert_all.sh (day-10 chain: vd → vc → vb → va → uy → uw → uv → uc → ub).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vd/vd_main.py 2>&1 | grep -E "VD |SAVED|Error|Traceback|REVERT" || true
echo "VD REVERT_ALL done (vd_obj/mats removed; UY W windows unhidden; cream/spandrel stash restored)"
