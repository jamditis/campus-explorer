cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 7000 ]; do sleep 10; done
echo "$(date +%T) GO"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws162d.blend WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_pre_20261115ws162.blend --python scripts/ws162/main162.py 2>&1 | grep -E "LOT|SHOULDER|pad|SAVED|rror|Trace|WATCH"
[ -e montclair_state_ws162d.blend ] || exit 2
echo "$(date +%T) fix done"
