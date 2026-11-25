#!/bin/bash
cd /workspace/nj-scenes/montclair-state
DLR=${DLR:-$(( $(date +%s) + 900 ))}
until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-4500} ]; do
  [ $(date +%s) -ge $DLR ] && { echo "$(date +%T) GATE TIMEOUT"; exit 3; }; sleep 3; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CHAIN="$CHAIN" INF="${INF:-$PWD/montclair_state.blend}" OUT=$PWD/$OUTN WD_MIN=${WDM:-1500} bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws208/merge208.py 2>&1 | grep -E "M2C242|F242|P242|F241|P241|M2B|M2C240|F240|P240|M2C239|F239|P239|F237|M2D|P238|F236|F236C|F236D|F236E|F235|OFF208|POKE208|SAVED|MEM208|rror|Trace|WATCH"
echo "$(date +%T) END"
