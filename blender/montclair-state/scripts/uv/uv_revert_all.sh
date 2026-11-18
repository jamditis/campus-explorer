#!/bin/bash
# Undo session uv (Freeman Hall day-10 first build). Run BEFORE uc_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uv/uv_main.py 2>&1 | grep -E "UV |SAVED|Error|Traceback|REVERT"
