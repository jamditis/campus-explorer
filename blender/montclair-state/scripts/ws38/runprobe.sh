#!/bin/bash
cd /workspace/nj-scenes/montclair-state
for i in $(seq 1 180); do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ $a -gt 6000 ] && break; sleep 5; done
echo "start avail=$a $(date)"
WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws38/probe.py 2>&1 | grep -v "^Read\|^Blender\|^$\|DEBUG\|^Info"
echo done $(date)
