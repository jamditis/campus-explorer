#!/bin/bash
# Undo session ui (Partridge Joe lawn strip). Run BEFORE uh_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ui/ui_main.py 2>&1 | grep -E "UI |SAVED|Error|Traceback|REVERT"
