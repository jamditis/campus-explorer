#!/bin/bash
cd /workspace/nj-scenes/montclair-state
for c in "$@"; do
 a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) R START $c $a"
 CAMS="$c" OUT_TAG=ws111 SAMP=${SAMP:-16} PCT=${PCT:-60} TEXLIM=${TEXLIM:-1024} WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup scripts/ws111/render_cut111.blend --python scripts/ws111/render111.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"
done
echo "$(date +%T) RENDER DONE"; echo END
