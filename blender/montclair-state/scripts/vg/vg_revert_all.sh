#!/bin/bash
# Undo session vg. Run BEFORE vf_revert_all.sh (day-10 chain: vg → vf → ve → vd → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vg/vg_main.py 2>&1 | grep -E "VG |SAVED|Error|Traceback|REVERT" || true
echo "VG REVERT_ALL done (vg_obj/mats removed; W/VB glass stash restored; UY S / UV E unhidden)"
