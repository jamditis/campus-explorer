cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5800 ]; do sleep 10; done
echo "$(date +%T) GO fix167"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws167a.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python-expr "import bpy,os;exec(open('/workspace/nj-scenes/montclair-state/scripts/ws167/fix167.py').read());bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep -E "LANE|BLEACH|GN|PROBE|EDGE|CAMS|SAVED|rror|Trace|WATCH"
[ -e montclair_state_ws167a.blend ] || exit 2
echo "$(date +%T) FIXDONE"
