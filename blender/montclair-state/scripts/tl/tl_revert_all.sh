#!/bin/bash
# tl revert: BLEND (default montclair_state.blend) -> pre-tl state. Saves in place. Run BEFORE any tk/tj revert.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tl/tl_trees.py 2>&1 | grep -E "TLT|SAVED|Error"
REVERT=1 SAVE=1 $B -b $F --python scripts/tl/tl_main.py 2>&1 | grep -E "TL|SAVED|Error"
