#!/bin/bash
# tk revert: BLEND (default montclair_state.blend) -> pre-tk state. Saves in place. Run BEFORE any tj revert (tk reuses TJ materials).
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tk/tk_main.py 2>&1 | grep -E "TK|SAVED|Error"
