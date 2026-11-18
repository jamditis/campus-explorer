cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5200 ]; do sleep 5; done
echo "$(date +%T) GO"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws160/fix160.py 2>&1 | grep --line-buffered -E "FIX160|rror|Trace|WATCH" | cut -c1-400
[ -e montclair_state_ws160a.blend ] || exit 2
echo "$(date +%T) fix done"
bash scripts/ws158/go158r.sh montclair_state_ws160a.blend ws160a wip
