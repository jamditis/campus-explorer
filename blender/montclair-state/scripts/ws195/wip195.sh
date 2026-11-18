cd /workspace/nj-scenes/montclair-state
until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${RGATE:-10000} ]; do sleep 5; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
T=$(date +%Y%m%d-%H%M) TAG=$TAG CAMS="$CAMS" DIR=${DIR:-wip} WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup $F --python scripts/ws195/wip195.py 2>&1 | grep -E "WROTE|MEM195|rror|Trace|WATCH"
echo "$(date +%T) END"
