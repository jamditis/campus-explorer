#!/bin/bash
# wait for MemAvailable >= 7000 MB (balloon release), then apply fix74b to MAIN; give up at 21:08 ET
cd /workspace/nj-scenes/montclair-state
while [ $(date +%H%M) -lt 2108 ]; do
 a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 if [ "$a" -ge 7000 ]; then echo "$(date +%T) avail $a -> apply"
   WD_MIN=1500 timeout 600 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws74/apply74b.py 2>&1 | grep -E "W74b (lot|ground|gb|cells|SAVED|NOT)|WATCH|rror" | cut -c1-300
   grep -q "" /dev/null; sha256sum montclair_state.blend; [ "$(stat -c %Y montclair_state.blend)" -gt $(( $(date +%s) - 120 )) ] && { echo APPLIED; exit 0; }
 fi; sleep 15; done; echo "$(date +%T) GAVE UP (memory)"
