#!/bin/bash
# Undo session vi. Run BEFORE vh_revert_all.sh (day-10 chain: vi → vh → vg → vf → ve → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vi/vi_main.py 2>&1 | grep -E "VI |SAVED|Error|Traceback|REVERT" || true
echo "VI REVERT_ALL done (vi_obj/mats removed; W/VB/SE glass + sky + span + VB cream + VH shadow stashes restored)"
