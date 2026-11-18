#!/bin/bash
# Undo session uf (day-9 soft-end fade + College Hall east arch polish).
# Run BEFORE ue_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/uf/uf_main.py 2>&1 | grep -E "UF |SAVED|Error|Traceback|REVERT"
