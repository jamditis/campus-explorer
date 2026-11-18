cd /workspace/nj-scenes/montclair-state
DL=$(date -d '01:02' +%s)
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 7800 ]; do [ $(date +%s) -ge $DL ] && { echo "$(date +%T) GATE TIMEOUT avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 3; }; sleep 5; done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws175a.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python-expr "import bpy,os;exec(open('/workspace/nj-scenes/montclair-state/scripts/ws175/band175.py').read());exec(open('/workspace/nj-scenes/montclair-state/scripts/ws175/fix175.py').read());exec(open('/workspace/nj-scenes/montclair-state/scripts/ws175/fix175b.py').read());exec(open('/workspace/nj-scenes/montclair-state/scripts/ws175/fix175c.py').read());bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep --line-buffered -E "FIX175|LIP175|STRIPE175|BAND175|SAVED|rror|Trace|WATCH"
echo "$(date +%T) END"
