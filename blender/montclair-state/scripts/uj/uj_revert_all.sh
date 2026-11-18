#!/bin/bash
# Undo session uj (Partridge leftover polish). Run BEFORE ui_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uj/uj_main.py 2>&1 | grep -E "UJ |SAVED|Error|Traceback|REVERT"
