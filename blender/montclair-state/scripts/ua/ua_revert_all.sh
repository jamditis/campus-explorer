#!/bin/bash
# Undo session ua (Normal Ave edge). Run BEFORE tz_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ua/ua_main.py 2>&1 | grep -E "UA |SAVED|Error|Traceback|REVERT"
