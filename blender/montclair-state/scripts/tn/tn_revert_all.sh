#!/bin/bash
# tn revert: run BEFORE any tm/tl/tk/tj revert. Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tn/tn_main.py 2>&1 | grep -E "TN|SAVED|Error"
