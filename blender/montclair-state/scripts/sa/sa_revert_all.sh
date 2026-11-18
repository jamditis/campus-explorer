#!/bin/bash
# sa full revert on a given blend (default main): lower2 -> cams -> annex -> lower. Pre-sa backup: montclair_state_pre_20261104sa.blend
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${1:-montclair_state.blend}
for s in sa_grass_on_paving sa_lower2 sa_cams sa_annex sa_lower; do REVERT=1 SAVE=1 $B -b $F --python scripts/sa/$s.py 2>&1 | grep -E "^SA|SAVED|rror"; done
