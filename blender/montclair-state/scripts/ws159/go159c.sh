cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5200 ]; do sleep 5; done
echo "$(date +%T) GO"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws159b.blend --python scripts/ws159/fix159c.py 2>&1 | grep --line-buffered -E "FIX159|rror|Trace|WATCH" | cut -c1-400
[ -e montclair_state_ws159c.blend ] || exit 2
echo "$(date +%T) fix done"
bash scripts/ws158/go158r.sh montclair_state_ws159c.blend ws159c wip
