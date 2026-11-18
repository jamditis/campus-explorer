#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" = "0112" ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 5200 ] && break; sleep 10; done
echo "$(date +%T) START $a"
SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws102/apply102.py 2>&1 | grep -E "A102|rror|Trace|WATCH|line [0-9]+"
sha256sum montclair_state.blend > scripts/ws102/sha_after.txt
echo "$(date +%T) APPLIED"
echo END
