#!/bin/bash
# memory-gated apply of ws89 A+B into main (main load ~2.4 GB; needs >5 GB available)
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" -ge ${GIVEUP:-1222} ] && { echo "$(date +%T) GAVE UP avail $a"; exit 1; }
 if [ "$a" -gt 5000 ]; then echo "$(date +%T) START avail $a"
  SAVE=1 DO=AB WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws89/apply89.py 2>&1 | grep -E "A89|rror|Trace|WATCH"
  sha256sum montclair_state.blend | cut -c1-64; echo "$(date +%T) END"; exit 0
 else sleep 15; fi; done
