#!/bin/bash
# usage: r.sh TAG DIR cam=label ...
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; TAG=$1; D=$2; shift 2
for cam in "$@"; do for try in 1 2 3; do
 a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) avail $a $cam"
 [ "$a" -lt ${GATE:-5800} ] && { sleep 45; continue; }
 out=$(DIR=$D CULL=-360,-150,-150,60 TEXLIM=1024 SAMP=${SAMP:-16} PCT=${PCT:-55} OUT_TAG=$TAG CAMS="$cam" WD_MIN=${WD_MIN:-1500} bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws72/render72.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
 echo "$out" | grep -q WROTE && break; sleep 20; done; done; echo "$(date +%T) done"
