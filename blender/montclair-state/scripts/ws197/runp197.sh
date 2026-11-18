cd /workspace/nj-scenes/montclair-state
FILE=$PWD/montclair_state.blend CHAIN="$1" WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws196/runp196.py 2>&1 | grep -E "P197|F197|V197|rror|Trace|WATCH"
