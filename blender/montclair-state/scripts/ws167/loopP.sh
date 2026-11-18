cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6500 ]; do sleep 10; done
echo "$(date +%T) GO probe"
WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws167/probe167.py 2>&1 | grep -E "MODS|^Y|rror|Trace|WATCH"
echo "$(date +%T) END"
