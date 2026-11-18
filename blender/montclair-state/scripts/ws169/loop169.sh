cd /workspace/nj-scenes/montclair-state
echo "$(date +%T) GO fix169 avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws169a.blend WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python-expr "import bpy,os;exec(open('/workspace/nj-scenes/montclair-state/scripts/ws169/fix169.py').read());exec(open('/workspace/nj-scenes/montclair-state/scripts/ws169/fix169b.py').read());bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep -E "BANK|PATCH|NEAR|LIGHT|SAVED|rror|Trace|WATCH"
echo "$(date +%T) END"
