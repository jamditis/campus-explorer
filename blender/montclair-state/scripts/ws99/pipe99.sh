#!/bin/bash
cd /workspace/nj-scenes/montclair-state
while :; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
 [ "$(date +%H%M)" -ge 2210 ] && { echo "GAVE UP $a"; echo END; exit 1; }
 [ "$a" -gt 6000 ] && break; sleep 10; done
echo "$(date +%T) START $a"
sha256sum montclair_state.blend > scripts/ws99/sha_before.txt
cp montclair_state.blend montclair_state_pre_20261112ws99.blend
SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws99/apply99.py 2>&1 | grep -E "A99|rror|Trace|WATCH"
sha256sum montclair_state.blend > scripts/ws99/sha_after.txt
echo "$(date +%T) APPLIED"
echo END
