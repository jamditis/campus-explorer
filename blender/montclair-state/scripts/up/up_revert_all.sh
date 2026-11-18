#!/bin/bash
# Undo session up (Partridge leftover polish). Run BEFORE uo_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/up/up_main.py 2>&1 | grep -E "UP |SAVED|Error|Traceback|REVERT"
