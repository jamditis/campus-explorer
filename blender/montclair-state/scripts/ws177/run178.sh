cd /workspace/nj-scenes/montclair-state
DL=$(date -d '04:05' +%s)
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 8500 ]; do [ $(date +%s) -ge $DL ] && { echo "$(date +%T) GATE TIMEOUT avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 3; }; sleep 5; done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
EXTRA="exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177b.py').read());exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177c.py').read());"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws177a.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python-expr "import bpy,os;exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177.py').read());$EXTRA bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep --line-buffered -E "FIX177|SAVED|rror|Trace|WATCH"
echo "$(date +%T) END"
