#!/bin/bash
# Undo session ty (Partridge approaches). Run BEFORE tx_revert_all.sh. BLEND defaults to main.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ty/ty_main.py 2>&1 | grep -E "TY|SAVED|Error|Traceback"
