#!/bin/bash
# Undo session uq (Partridge leftover polish). Run BEFORE up_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uq/uq_main.py 2>&1 | grep -E "UQ |SAVED|Error|Traceback|REVERT"
