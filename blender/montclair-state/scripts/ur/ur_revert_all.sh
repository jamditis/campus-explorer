#!/bin/bash
# Undo session ur (Partridge leftover polish). Run BEFORE uq_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ur/ur_main.py 2>&1 | grep -E "UR |SAVED|Error|Traceback|REVERT"
