#!/bin/bash
# Undo session uo (Partridge leftover polish). Run BEFORE un_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uo/uo_main.py 2>&1 | grep -E "UO |SAVED|Error|Traceback|REVERT"
