#!/bin/bash
# ws59b: when MemAvailable>5800 and main not open: apply autumn palette v2 (scripts/ws59/apply.py), then run the ws59 render gate (v2 WIPs). To 11:00. No lock.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
while [ "$(date +%H%M)" -lt 1100 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 5800 ] && ! pgrep -f "blender -b montclair_state.blend" >/dev/null; then
    echo "$(date +%T) avail $a apply v2"
    out=$(WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws59/apply.py 2>&1 | grep -E "A59|WATCHDOG|rror"); echo "$out"
    if echo "$out" | grep -q "A59 saved"; then echo "V2 saved $(sha256sum montclair_state.blend|cut -c1-16)"; exec bash scripts/ws59/gate.sh; fi
    sleep 90
  fi
  sleep 20
done
echo "$(date +%T) gate_b end (v2 not applied)"
