cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5800 ]; do sleep 10; done
echo "$(date +%T) GO b"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws167b.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws167a.blend --python-expr "import bpy,os;exec(open('/workspace/nj-scenes/montclair-state/scripts/ws167/fix167b.py').read());bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep -E "^B |LANE|PROBE|SAVED|rror|Trace|WATCH"
[ -e montclair_state_ws167b.blend ] || exit 2
echo "$(date +%T) FIXDONE"
for c in WS162_CAM_oblique_Lot3_from_W_high=oblique_Lot3_W_bank_bleachers_lane_from_W_high WS167_CAM_eye_lane_N_along_bleachers_from_S=eye_Sprague_lane_N_along_bleachers_from_S WS162_CAM_eye_Lot3_from_Sprague_walk_NW=eye_Lot3_W_bleachers_from_Sprague_walk_NW WS167_CAM_closeup_bleachers_from_W_turf=closeup_bleachers_from_W; do
 until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5800 ]; do sleep 10; done
 CULL=-380,-240,-300,-140 DIR=wip OUT_TAG=ws167b bash scripts/ws166/rt.sh montclair_state_ws167b.blend $c
done
echo "$(date +%T) ALL DONE"
