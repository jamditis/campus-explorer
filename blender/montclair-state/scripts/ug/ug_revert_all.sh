#!/bin/bash
# Undo session ug (Partridge E-side DTM seam fill + approach cleanup). Run BEFORE uf_revert_all.sh.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b "$F" --python scripts/ug/ug_main.py 2>&1 | grep -E "UG |SAVED|Error|Traceback|REVERT"
