#!/bin/bash
# Undo session tx (Partridge/Nursing massing + TX cams). Run BEFORE tw_revert_all.sh. BLEND defaults to main.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tx/tx_main.py 2>&1 | grep -E "TX|SAVED|Error|Traceback"
