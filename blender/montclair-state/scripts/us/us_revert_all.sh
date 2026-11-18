#!/bin/bash
# Undo session us (Partridge leftover polish). Run BEFORE ur_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/us/us_main.py 2>&1 | grep -E "US |SAVED|Error|Traceback|REVERT"
