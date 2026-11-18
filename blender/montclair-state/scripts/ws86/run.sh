#!/bin/bash
cd /workspace/nj-scenes/montclair-state
SAVE=${SAVE:-0} WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws86/$1 2>&1 | grep -E "A86|V86|R86|P86|rror|Trace|WATCH"
