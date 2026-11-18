#!/bin/bash
# Undo session vs (restores glass/sky values, unhides 90 VJ..VR W interbay overlays, restores N entrance cam). Run BEFORE vr_revert_all.sh.
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 /workspace/opt/blender/blender -b "$F" --python scripts/vs/vs_main.py 2>&1 | grep -E "VS |SAVED|Error|Traceback" || true
