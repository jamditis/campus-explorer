#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" \> "0220" ] && { echo "$(date +%T) GAVE UP avail=$a"; echo END; exit 1; }
 [ "$a" -gt 6000 ] && break; sleep 10; done
echo "$(date +%T) START $a"
cp montclair_state.blend montclair_state_pre_20261113ws103.blend
SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws102/terr102b.py 2>&1 | grep -E "S102|rror|Trace|WATCH"
sha256sum montclair_state.blend > scripts/ws103/sha_after.txt
echo "$(date +%T) APPLIED"; echo END
