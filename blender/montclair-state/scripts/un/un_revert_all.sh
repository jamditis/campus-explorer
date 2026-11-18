#!/bin/bash
# Undo session un (Partridge leftover polish). Run BEFORE um_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/un/un_main.py 2>&1 | grep -E "UN |SAVED|Error|Traceback|REVERT"
