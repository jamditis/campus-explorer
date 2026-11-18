#!/bin/bash
# Undo session vf. Run BEFORE ve_revert_all.sh (day-10 chain: vf → ve → vd → vc → vb → va → uy → …).
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 "$B" -b "$F" --python scripts/vf/vf_main.py 2>&1 | grep -E "VF |SAVED|Error|Traceback|REVERT" || true
echo "VF REVERT_ALL done (vf_obj/mats removed; glass/spandrel/frame/reveal stash restored)"
