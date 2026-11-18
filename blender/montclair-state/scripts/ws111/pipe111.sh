#!/bin/bash
cd /workspace/nj-scenes/montclair-state
a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) MAIN START $a"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws111/${1:-main111.py} 2>&1 | grep -E "E111|F111|G111|CUT|rror|Trace|WATCH|line "
sha256sum montclair_state.blend | cut -c1-16; echo "$(date +%T) DONE"; echo END
