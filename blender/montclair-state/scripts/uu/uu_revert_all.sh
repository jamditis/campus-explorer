#!/bin/bash
# Undo session uu (Partridge leftover polish). Run BEFORE ut_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uu/uu_main.py 2>&1 | grep -E "UU |SAVED|Error|Traceback|REVERT"
