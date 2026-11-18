#!/bin/bash
cd /workspace/nj-scenes/montclair-state
for i in $(seq 1 80); do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); echo "$(date +%T) avail $a"
 if [ "$a" -ge ${GATE:-7000} ]; then
  out=$(APPLYF=${APPLYF:-apply77a.py} WD_MIN=1500 timeout 900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws77/save_apply.py 2>&1 | grep -E "WS77|SAVED|WATCHDOG|rror"); echo "$out"
  echo "$out" | grep -q SAVED && { echo DONE; exit 0; }; fi; sleep 20; done
