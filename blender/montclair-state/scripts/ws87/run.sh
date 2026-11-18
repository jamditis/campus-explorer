#!/bin/bash
cd /workspace/nj-scenes/montclair-state
SAVE=${SAVE:-0} WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws87/$1 2>&1 | grep -E "A87|V87|R87|P87|rror|Trace|WATCH"
