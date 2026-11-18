cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4000 ] && ! pgrep -x blender >/dev/null; do sleep 2; done
FILE=$PWD/${F:-montclair_state.blend} CHAIN="$1" WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws196/runp196.py 2>&1 | grep -E "P198|F198|V198|rror|Trace|WATCH"
