#!/bin/bash
# ws60: after the ws59 render gate ends, when MemAvailable>5800 and main not open: backup main, add terrain-edge apron, then render 4 WIPs. To 13:00. No lock.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
log(){ echo "$(date +%T) $*"; }
while pgrep -f "scripts/ws59/gate" >/dev/null && [ "$(date +%H%M)" -lt 1300 ]; do sleep 30; done
applied=0
while [ $applied -eq 0 ] && [ "$(date +%H%M)" -lt 1300 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 5800 ] && ! pgrep -f "blender -b montclair_state.blend" >/dev/null; then
    [ -f montclair_state_pre_20261111ws60.blend ] || cp montclair_state.blend montclair_state_pre_20261111ws60.blend
    log "avail $a apply apron"
    out=$(WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws60/apply60.py 2>&1 | grep -E "A60|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -qE "A60 (saved|already)" && { applied=1; log "C60 saved $(sha256sum montclair_state.blend|cut -c1-16)"; echo "- ws60 gate $(date '+%I:%M %p') ET: terrain-edge apron applied to main ($(sha256sum montclair_state.blend|cut -c1-16)); revert scripts/ws60/ws60_revert_all.sh" >> /workspace/nj-scenes/LOG.md; break; }
    sleep 90
  fi
  sleep 20
done
[ $applied -eq 1 ] || { log "gate60 end (not applied)"; exit; }
sed -e 's/1100/1300/g' -e 's/GOLDEN_ws59_goldenhour/GOLDEN_ws60_goldenhour/' -e 's/ws59 render gate/ws60 render gate/' -e 's#scripts/ws59/gate.log#scripts/ws60/gate.log#' scripts/ws59/gate.sh > scripts/ws60/render_gate.sh
exec bash scripts/ws60/render_gate.sh
