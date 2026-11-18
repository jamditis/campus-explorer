cd /workspace/nj-scenes/montclair-state
until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 7000 ]; do sleep 5; done
echo "$(date +%T) GO fix171 avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws171a.blend WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws170a.blend --python-expr "import bpy,os;exec(open('/workspace/nj-scenes/montclair-state/scripts/ws171/probe171.py').read());exec(open('/workspace/nj-scenes/montclair-state/scripts/ws171/fix171.py').read());bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep -E "PROBE|TREE|SAVED|rror|Trace|WATCH"
echo "$(date +%T) END"
