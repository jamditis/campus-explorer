#!/bin/bash
# Undo session ul (Partridge leftover polish). Run BEFORE uk_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ul/ul_main.py 2>&1 | grep -E "UL |SAVED|Error|Traceback|REVERT"
