#!/bin/bash
cd /workspace/nj-scenes/montclair-state
for i in $(seq 1 240); do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ $a -gt 5500 ] && break; sleep 5; done
echo "start avail=$a $(date)"
SAVE=1 WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws38/fix.py 2>&1 | grep -E "W38|rror|Traceback|line [0-9]|WATCHDOG"
echo done $(date)
