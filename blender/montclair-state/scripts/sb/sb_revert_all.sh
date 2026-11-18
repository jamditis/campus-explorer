#!/bin/bash
# sb full revert on a given blend (default main): dtm_tone -> lawn -> cams -> main. Pre-sb backup: montclair_state_pre_20261104sb.blend
# Test reverts in this directory, never /tmp (relative library paths).
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${1:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/sb/sb_dtm_tone.py --python scripts/sb/sb_lawn.py --python scripts/sb/sb_cams.py --python scripts/sb/sb_main.py 2>&1 | grep -E "^SB|SAVED|rror"
