#!/bin/bash
# Undo session uh (Partridge leftover polish). Run BEFORE ug_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uh/uh_main.py 2>&1 | grep -E "UH |SAVED|Error|Traceback|REVERT"
