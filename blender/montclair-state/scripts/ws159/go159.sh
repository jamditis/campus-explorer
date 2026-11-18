cd /workspace/nj-scenes/montclair-state
DEAD=$(date -d 'today 08:58' +%s)
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5200 ]; do [ $(date +%s) -ge $DEAD ] && { echo "$(date +%T) NOGO memory"; exit 1; }; sleep 5; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
[ -e montclair_state_pre_20261115ws159.blend ] || cp -p montclair_state.blend montclair_state_pre_20261115ws159.blend
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws159/fix159.py 2>&1 | grep --line-buffered -E "FIX159|rror|Trace|WATCH" | cut -c1-400
[ -e montclair_state_ws159a.blend ] || exit 2
echo "$(date +%T) fix done"
bash scripts/ws158/go158r.sh montclair_state_ws159a.blend ws159a wip
