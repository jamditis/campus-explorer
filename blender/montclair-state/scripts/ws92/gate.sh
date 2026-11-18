#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" -ge 1500 ] && { echo "GAVE UP $a"; exit 1; }
 if [ "$a" -gt 5000 ]; then echo "$(date +%T) START $a"
  WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws92/$1 2>&1 | grep -E "P92|rror|Trace|WATCH"
  break; else sleep 10; fi; done; echo "$(date +%T) END"
