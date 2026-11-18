#!/bin/bash
# Undo session tz (College Hall E/N + north addition). Run BEFORE ty_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/tz/tz_cams.py 2>&1 | grep -E "TZ|SAVED|Error|Traceback|REVERT"
REVERT=1 SAVE=1 $B -b "$F" --python scripts/tz/tz_main.py 2>&1 | grep -E "TZ|SAVED|Error|Traceback|REVERT"
