#!/bin/bash
# Undo session ud (day-9 Normal Ave asphalt tone + Partridge walk edge polish).
# Run BEFORE uc_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ud/ud_main.py 2>&1 | grep -E "UD |SAVED|Error|Traceback|REVERT"
