#!/bin/bash
cd /workspace/nj-scenes/montclair-state
a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) MAIN START $a"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws112/${1:-main112.py} 2>&1 | grep -E "P112|E112|rror|Trace|WATCH|line "
sha256sum montclair_state.blend | cut -c1-16; echo "$(date +%T) DONE"; echo END
