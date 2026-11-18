cd /workspace/nj-scenes/montclair-state
until ! pgrep -f loop166b.sh >/dev/null; do sleep 5; done
[ -e montclair_state_ws166b.blend ] && B=montclair_state_ws166b.blend || B=montclair_state_ws166a.blend
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6000 ]; do sleep 10; done
echo "$(date +%T) GO fix c on $B"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws166c.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup $B --python-expr "import bpy,os;exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/fix166c.py').read());bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True);print('SAVED',flush=True)" 2>&1 | grep -E "TREEC|SAVED|rror|Trace|WATCH"
[ -e montclair_state_ws166c.blend ] || exit 2
for c in WS165_CAM_eye_aisle_mouth_tree_from_Normal_Ave_SE=eye_NormalAve_N_tree_row_from_SE WS163_CAM_oblique_NormalAve_W_LotS_from_SW=oblique_NormalAve_W_tree_row_from_SW WS163_CAM_eye_NormalAve_W_from_E_walk=eye_NormalAve_W_from_E_walk WS165_CAM_closeup_bed_front_at_walk_from_SE=closeup_bed_tree_E_edge_from_SE; do
 until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6500 ]; do sleep 10; done
 CULL=-380,-240,-300,-140 DIR=wip OUT_TAG=ws166c bash scripts/ws166/rt.sh montclair_state_ws166c.blend $c
done
echo "$(date +%T) ALL DONE c"
