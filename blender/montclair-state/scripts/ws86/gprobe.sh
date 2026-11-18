#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" -ge 0930 ] && { echo "GAVE UP $a"; exit 1; }
 if [ "$a" -gt 5000 ]; then echo "$(date +%T) START $a"
  WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws86/$1 2>&1 | grep -E "P8.|A86|V86|rror|Trace|WATCH"
  grep -q WATCH <(tail -1 /dev/null) ; break; else sleep 10; fi; done; echo "$(date +%T) END"
