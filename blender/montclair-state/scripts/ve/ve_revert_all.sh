#!/bin/bash
# Undo session ve. Run BEFORE vd_revert_all.sh (day-10 chain: ve → vd → vc → vb → va → uy → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/ve/ve_main.py 2>&1 | grep -E "VE |SAVED|Error|Traceback|REVERT" || true
echo "VE REVERT_ALL done (ve_obj/mats removed; W/S cream slots restored; glass/spandrel/RTU stash restored)"
