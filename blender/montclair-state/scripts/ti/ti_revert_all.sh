#!/bin/bash
# ti revert: BLEND (default montclair_state.blend) -> pre-ti state. Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/ti/ti_main.py 2>&1 | grep -E "TI |SAVED|Error"
