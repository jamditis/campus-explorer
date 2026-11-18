#!/bin/bash
# Undo session tw (run BEFORE tv_revert_all.sh). BLEND defaults to main.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tw/tw_main.py 2>&1 | grep -E "TW|SAVED|Error|Traceback|REVERT"
REVERT=1 SAVE=1 $B -b $F --python scripts/tw/tw_cams.py 2>&1 | grep -E "TW|SAVED|Error|Traceback|REVERT"
