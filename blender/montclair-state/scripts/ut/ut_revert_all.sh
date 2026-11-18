#!/bin/bash
# Undo session ut (Partridge leftover polish). Run BEFORE us_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ut/ut_main.py 2>&1 | grep -E "UT |SAVED|Error|Traceback|REVERT"
