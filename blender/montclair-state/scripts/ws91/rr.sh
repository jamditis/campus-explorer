#!/bin/bash
cd /workspace/nj-scenes/montclair-state
a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) avail $a"
DIR=${DIR:-wip} CULL=${CULL:--360,-150,-150,60} TEXLIM=1024 SAMP=${SAMP:-16} PCT=${PCT:-55} OUT_TAG=${OUT_TAG:-ws91} CAMS="$1" WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws91/render91.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"
echo "$(date +%T) done"
