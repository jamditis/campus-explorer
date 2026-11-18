#!/bin/bash
# tj revert: BLEND (default montclair_state.blend) -> pre-tj state. Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tj/tj_lawn.py --python scripts/tj/tj_main.py 2>&1 | grep -E "TJ|SAVED|Error"
