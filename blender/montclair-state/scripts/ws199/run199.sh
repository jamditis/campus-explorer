#!/bin/bash
# ws189 merge gate: merge188 path still evaluates the full skirt stack at SAVE (after restore) -> needs ~8.5 GB avail
cd /workspace/nj-scenes/montclair-state
DLR=${DLR:-$(( $(date +%s) + 1200 ))}
until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-4500} ]; do
  [ $(date +%s) -ge $DLR ] && { echo "$(date +%T) GATE TIMEOUT"; exit 3; }; sleep 3; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CHAIN="${CHAIN:-ws189/fix189.py}" OUT=$PWD/${OUTN:-montclair_state_ws189a.blend} WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws189/merge189.py 2>&1 | grep -E "F198|F199|F199b|F199c|F199d|FIX19|FIX189|POKE189|SKIRT188 OFF|SAVED|MEM188|rror|Trace|WATCH"
( while pgrep -x blender >/dev/null; do sleep 1; done ) ; echo "$(date +%T) END"
