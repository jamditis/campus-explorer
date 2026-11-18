#!/bin/bash
# Undo session uc (Finley wall tops + Freeman parapet + UC cams). Run BEFORE ub_revert_all.sh. BLEND defaults to main.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uc/uc_main.py 2>&1 | grep -E "UC |SAVED|Error|Traceback"
