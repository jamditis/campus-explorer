#!/bin/bash
# Revert session tu (Blanton entrance bays). Run BEFORE scripts/tt/tt_revert_all.sh.
cd /workspace/nj-scenes/montclair-state && REVERT=1 SAVE=1 /workspace/opt/blender/blender -b montclair_state.blend --python scripts/tu/tu_main.py
