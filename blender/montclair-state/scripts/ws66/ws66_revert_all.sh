#!/bin/bash
# revert ws66 (Red Hawk Deck appended from the north file): restore the pre-ws66 backup (= ws64 5d5485c6)
cd /workspace/nj-scenes/montclair-state && cp montclair_state_pre_20261111ws66.blend montclair_state.blend && echo "reverted to pre-ws66"
# alternative that keeps later work: REVERT=1 /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws66/apply66.py
