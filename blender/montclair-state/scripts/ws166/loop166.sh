cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6000 ]; do sleep 10; done
echo "$(date +%T) GO fix"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws166a.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws166/main166.py 2>&1 | grep -E "EDGE166|GROUND166|LIP166|SAVED|rror|Trace|WATCH"
[ -e montclair_state_ws166a.blend ] || exit 2
echo "$(date +%T) fix done"
for c in WS165_CAM_closeup_bed_front_at_walk_from_SE=closeup_bed_E_edge_spur_from_SE WS163_CAM_oblique_NormalAve_W_LotS_from_SW=oblique_NormalAve_W_LotS_from_SW WS165_CAM_eye_aisle_mouth_tree_from_Normal_Ave_SE=eye_aisle_mouth_bed_from_NormalAve_SE WS163_CAM_eye_NormalAve_W_from_E_walk=eye_NormalAve_W_from_E_walk; do
 until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6500 ]; do sleep 10; done
 CULL=-380,-240,-300,-140 DIR=wip OUT_TAG=ws166a bash scripts/ws166/rt.sh montclair_state_ws166a.blend $c
done
echo "$(date +%T) ALL DONE"
