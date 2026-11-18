# ws186 gated merge on main ws184a: chain = scripts/ws186/chain.txt (fix185 + fix186) -> montclair_state_ws186a.blend
# -> montclair_state_ws186a.blend when MemAvailable >= 8500 MB AND no other blender running (until $DLT). Does NOT touch .lock.
cd /workspace/nj-scenes/montclair-state
DL=$(date -d "${DLT:-06:10}" +%s)
av(){ awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo; }
until [ $(av) -ge 8500 ] && ! pgrep -x blender >/dev/null; do [ $(date +%s) -ge $DL ] && { echo "$(date +%T) GATE TIMEOUT avail=$(av)"; exit 3; }; sleep 5; done
echo "$(date +%T) GO avail=$(av)"
S=/workspace/nj-scenes/montclair-state/scripts
EX=""; for f in $(grep -v '^#' scripts/ws186/chain.txt); do EX="$EX exec(open('$S/$f').read());"; done
echo "CHAIN: $(grep -v '^#' scripts/ws186/chain.txt | tr '\n' ' ')"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws186a.blend WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python-expr "import bpy,os;$EX bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep --line-buffered -E "FIX18|FIX186B|PROBE179|SAVED|rror|Trace|WATCH"
echo "$(date +%T) END"
