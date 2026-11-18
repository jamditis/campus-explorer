cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-3000} ] && ! pgrep -x blender >/dev/null; do sleep 2; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
FILE=$PWD/${F:-montclair_state.blend} CHAIN="$1" WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws196/runp196.py --python scripts/ws201/${P:-probe200.py} 2>&1 | grep -E "P200|F202|F201|F200|V200|rror|Trace|WATCH"
