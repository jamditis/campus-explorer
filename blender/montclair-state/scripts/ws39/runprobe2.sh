#!/bin/bash
cd /workspace/nj-scenes/montclair-state
for i in $(seq 1 120); do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ $a -gt 3000 ] && break; sleep 5; done
echo "start avail=$a $(date)"
WD_MIN=700 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws39/probe2.py 2>&1 | grep -E "P39|rror|WATCHDOG"
echo done $(date)
