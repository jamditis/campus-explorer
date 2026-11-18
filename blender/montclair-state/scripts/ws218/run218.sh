#!/bin/bash
cd /workspace/nj-scenes/montclair-state
DLR=${DLR:-$(( $(date +%s) + 900 ))}
until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-3000} ]; do
  [ $(date +%s) -ge $DLR ] && { echo "$(date +%T) GATE TIMEOUT"; exit 3; }; sleep 3; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CHAIN="$CHAIN" OUT=$PWD/$OUTN WD_MIN=${WDM:-1200} bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws208/merge208.py 2>&1 | grep -E "F218C|M2A|F217|F217d|F216|F207|F208|F210|F211|OFF208|POKE208|SAVED|MEM208|rror|Trace|WATCH"
echo "$(date +%T) END"
