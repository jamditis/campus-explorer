#!/bin/bash
# wait until MemAvailable > 4800 MB then run apply82a on main (watchdog 900); give up at 05:22
cd /workspace/nj-scenes/montclair-state
while :; do
 a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); now=$(date +%H%M)
 [ "$now" -ge 0522 ] && { echo "$(date +%T) GAVE UP avail=$a"; exit 1; }
 if [ "$a" -gt ${GATE:-4800} ]; then
  echo "$(date +%T) START avail=$a"
  WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws82/apply82a.py 2>&1 | grep -E "WS82a|rror|Trace|WATCHDOG"
  sha256sum montclair_state.blend; grep -q . <(sha256sum montclair_state.blend | grep -v a0235d54) && { echo "$(date +%T) APPLIED"; exit 0; }
  sleep 20
 else sleep 10; fi
done
