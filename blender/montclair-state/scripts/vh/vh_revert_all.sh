#!/bin/bash
# Undo session vh. Run BEFORE vg_revert_all.sh (day-10 chain: vh → vg → vf → ve → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vh/vh_main.py 2>&1 | grep -E "VH |SAVED|Error|Traceback|REVERT" || true
echo "VH REVERT_ALL done (vh_obj/mats removed; W/VB/SE glass + sky + span stashes restored)"
