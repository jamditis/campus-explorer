#!/bin/bash
# Revert session ts (NAIP skirt/far-field swap, skirt IOR, far-field skirt hole). Run BEFORE scripts/tr/tr_revert_all.sh.
cd /workspace/nj-scenes/montclair-state && REVERT=1 /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ts/ts_cam.py && REVERT=1 SAVE=1 /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ts/ts_main.py
