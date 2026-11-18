#!/bin/bash
# sc full revert on a given blend (default main): lawn -> dtm_tone (no-op, already reverted) -> main (joint mats, UVs, soil strips, cam).
# Pre-sc backup: montclair_state_pre_20261104sc.blend. Test reverts in this directory, never /tmp (relative library paths).
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${1:-montclair_state.blend}
REVERT=1 SCSAVE=1 $B -b $F --python scripts/sc/sc_lawn.py --python scripts/sc/sc_dtm_tone.py --python scripts/sc/sc_main.py 2>&1 | grep -E "^SC|SAVED|rror"
