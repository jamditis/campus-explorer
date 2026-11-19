#!/bin/bash
cd /workspace/nj-scenes/montclair-state
DLR=${DLR:-$(( $(date +%s) + 900 ))}
until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-4500} ]; do
  [ $(date +%s) -ge $DLR ] && { echo "$(date +%T) GATE TIMEOUT"; exit 3; }; sleep 3; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CHAIN="$CHAIN" INF="${INF:-$PWD/montclair_state.blend}" OUT=$PWD/$OUTN WD_MIN=${WDM:-1500} bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws208/merge208.py 2>&1 | grep -E "M2B|F235|F234|OFF208|POKE208|SAVED|MEM208|rror|Trace|WATCH"
echo "$(date +%T) END"
