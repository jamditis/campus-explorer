#!/bin/bash
# Undo session ub (Freeman Hall wall tops lifted to roof). Run BEFORE ua_revert_all.sh. BLEND defaults to main.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ub/ub_main.py 2>&1 | grep -E "UB |SAVED|Error|Traceback"
