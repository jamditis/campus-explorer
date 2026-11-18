#!/bin/bash
# tp revert: run BEFORE any tn/tm/tl/tk/tj revert. Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tp/tp_main.py 2>&1 | grep -E "TP|SAVED|Error"
