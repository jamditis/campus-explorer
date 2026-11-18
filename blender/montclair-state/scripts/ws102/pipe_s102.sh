#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" = "0118" ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 5600 ] && break; sleep 5; done
echo "$(date +%T) START $a"
SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws102/terr102b.py 2>&1 | grep -E "S102|rror|Trace|WATCH"
sha256sum montclair_state.blend > scripts/ws102/sha_after4.txt; echo "$(date +%T) $(cut -c1-16 scripts/ws102/sha_after4.txt)"; echo END
