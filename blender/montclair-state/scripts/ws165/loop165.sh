cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6000 ]; do sleep 10; done
echo "$(date +%T) GO fix"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws165a.blend WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws165/main165.py 2>&1 | grep -E "MULCH|CURB|ground|TREE|LEAF|SAVED|rror|Trace|WATCH"
[ -e montclair_state_ws165a.blend ] || exit 2
echo "$(date +%T) fix done"
for c in WS165_CAM_closeup_bed_front_at_walk_from_SE=closeup_bed_front_at_walk_from_SE WS165_CAM_eye_aisle_mouth_tree_from_Normal_Ave_SE=eye_aisle_mouth_tree_from_NormalAve_SE WS163_CAM_oblique_NormalAve_W_LotS_from_SW=oblique_NormalAve_W_LotS_from_SW WS163_CAM_eye_NormalAve_W_from_E_walk=eye_NormalAve_W_from_E_walk WS163_CAM_eye_Lot3_aisle_drive_from_NormalAve_S=eye_Lot3_aisle_drive_from_NormalAve_S; do
 until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 6500 ]; do sleep 10; done
 CULL=-380,-240,-300,-140 DIR=wip OUT_TAG=ws165a bash scripts/ws165/rt.sh montclair_state_ws165a.blend $c
done
echo "$(date +%T) ALL DONE"
