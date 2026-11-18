cd /workspace/nj-scenes/montclair-state
until ! pgrep -f loop166.sh >/dev/null; do sleep 5; done
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6000 ]; do sleep 10; done
echo "$(date +%T) GO fix b"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws166b.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws166a.blend --python-expr "import bpy,os;exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/fix166b.py').read());bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep -E "BANK166|SAVED|rror|Trace|WATCH"
[ -e montclair_state_ws166b.blend ] || exit 2
for c in WS162_CAM_eye_Lot3_from_Sprague_walk_NW=eye_Lot3_W_bank_from_Sprague_walk_NW WS162_CAM_oblique_Lot3_from_W_high=oblique_Lot3_W_bank_from_W_high; do
 until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6500 ]; do sleep 10; done
 CULL=-380,-240,-300,-140 DIR=wip OUT_TAG=ws166b bash scripts/ws166/rt.sh montclair_state_ws166b.blend $c
done
echo "$(date +%T) ALL DONE b"
