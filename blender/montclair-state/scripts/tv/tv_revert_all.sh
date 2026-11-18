#!/bin/bash
# Undo session tv (run BEFORE tu_revert_all.sh). BLEND defaults to main.
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/tv/tv_grass.py
REVERT=1 SAVE=1 $B -b $F --python scripts/tv/tv_cam.py
