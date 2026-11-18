#!/bin/bash
# ws65 render-only gate (no lock): is the "ghost box" east of Kasser in the ws64 oblique pre-existing? render same camera on the pre-ws64 backup; MemAvailable>5500; to 13:30
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
while [ "$(date +%H%M)" -lt 1330 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 5500 ] && ! pgrep -f "blender -b montclair_state" >/dev/null; then
    echo "$(date +%T) avail $a — render oblique on pre-ws64"
    out=$(DIR=test CULL=-320,-140,-90,110 TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=BEFORE_ws64 CAMS="WS64_CAM_oblique_Kasser_north=oblique_Kasser_north_before" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state_pre_20261111ws64.blend --python scripts/ws64/render64.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && { echo "- ws65 gate $(date '+%I:%M %p') ET: rendered pre-ws64 oblique for the ghost-box check (renders/test/*oblique_Kasser_north_before*)" >> /workspace/nj-scenes/LOG.md; break; }
    sleep 90; continue
  fi
  sleep 30
done
echo "$(date +%T) gate end"
