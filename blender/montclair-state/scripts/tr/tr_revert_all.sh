#!/bin/bash
# tr revert: run BEFORE any tq/tp/tn/tm/tl/tk/tj revert. Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tr/tr_main.py 2>&1 | grep -E "TR |SAVED|Error|Traceback"
