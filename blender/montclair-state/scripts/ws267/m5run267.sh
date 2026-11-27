#!/bin/bash
# ws267: rerun ws264 pre-release check on current main, gated at >= 7 GB MemAvailable, until DEADLINE (epoch)
cd /workspace/nj-scenes/montclair-state
until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-7000} ]; do
  [ $(date +%s) -ge ${DEADLINE:-9999999999} ] && { echo "$(date +%T) GATE NEVER OPENED (deadline)"; exit 3; }; sleep 3; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup ${INF:-montclair_state.blend} --python scripts/ws264/m5check264.py 2>&1 | grep -E "M5C264|rror|Trace|WATCH"
echo "done $(date +%T)"
