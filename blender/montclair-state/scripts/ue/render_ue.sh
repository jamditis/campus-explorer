#!/bin/bash
# Render one UE camera. Usage: render_ue.sh CAM_NAME OUT.jpg
set -e
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
CAM="$1"; OUT="$2"
export CAM OUT
$B -b montclair_state.blend -P scripts/ue/ue_render_one.py 2>&1 | grep -E "Saved|Error|Traceback|Render|UE_|cannot|not found" || true
