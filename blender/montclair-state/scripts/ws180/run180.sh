# ws180 gated merge: ws177 (3) + ws178 + ws179 + ws180 fixes -> montclair_state_ws180a.blend when MemAvailable >= 8.5 GB (until $DLT, default 06:10)
cd /workspace/nj-scenes/montclair-state
DL=$(date -d "${DLT:-06:10}" +%s)
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 8500 ]; do [ $(date +%s) -ge $DL ] && { echo "$(date +%T) GATE TIMEOUT avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 3; }; sleep 5; done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
S=/workspace/nj-scenes/montclair-state/scripts
EX=""; for f in ws177/fix177.py ws177/fix177b.py ws177/fix177c.py ws178/fix178.py ws179/fix179.py ws180/fix180.py ws180/fix180b.py ws179/probe179.py; do EX="$EX exec(open('$S/$f').read());"; done
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws180a.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python-expr "import bpy,os;$EX bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep --line-buffered -E "FIX17|FIX18|PROBE179|SAVED|rror|Trace|WATCH"
echo "$(date +%T) END"
