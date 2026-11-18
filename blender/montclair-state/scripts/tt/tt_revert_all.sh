#!/bin/bash
# Revert session tt (FARV / optional env knobs). Run BEFORE scripts/ts/ts_revert_all.sh.
cd /workspace/nj-scenes/montclair-state && REVERT=1 SAVE=1 /workspace/opt/blender/blender -b montclair_state.blend --python scripts/tt/tt_main.py
