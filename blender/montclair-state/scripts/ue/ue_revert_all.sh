#!/bin/bash
# Undo session ue (College Hall east). Run BEFORE ud_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ue/ue_cams.py 2>&1 | grep -E "UE|SAVED|Error|Traceback|REVERT"
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ue/ue_main.py 2>&1 | grep -E "UE|SAVED|Error|Traceback|REVERT"
