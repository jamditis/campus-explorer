#!/bin/bash
# Run BEFORE uy_revert_all.sh: va changes only the UV Freeman sign font object.
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
BLEND=${BLEND:-montclair_state.blend} REVERT=1 SAVE=1 /workspace/opt/blender/blender -b "$BLEND" --python scripts/va/va_fix_lettering.py
