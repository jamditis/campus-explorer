#!/bin/bash
# Undo session um (Partridge leftover polish). Run BEFORE ul_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/um/um_main.py 2>&1 | grep -E "UM |SAVED|Error|Traceback|REVERT"
