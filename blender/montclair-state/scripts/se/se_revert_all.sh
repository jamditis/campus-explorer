#!/bin/bash
# se revert: BLEND (default montclair_state.blend) -> pre-se state (removes SE roof collection + 2 SE cameras, restores the membrane material). Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/se/se_roof.py 2>&1 | grep -E "SE_|Error"
