#!/bin/bash
cd /workspace/nj-scenes/montclair-state
a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) RENDER START $a"
CAMS="$1" OUT_TAG=ws110 SAMP=${SAMP:-24} WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup scripts/ws110/render_cut110.blend --python scripts/ws110/render110.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"
echo "$(date +%T) RENDER DONE"; echo END
