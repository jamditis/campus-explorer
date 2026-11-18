cd /workspace/nj-scenes/montclair-state
for c in WS162_CAM_eye_Lot3_from_Sprague_walk_NW=eye_Lot3_W_bleachers_from_Sprague_walk_NW WS167_CAM_eye_lane_N_along_bleachers_from_S=eye_Sprague_lane_N_along_bleachers_from_S; do
 until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 8000 ]; do sleep 10; done
 echo "$(date +%T) R $c"
 CULL=-380,-240,-300,-140 DIR=wip OUT_TAG=ws167c bash scripts/ws166/rt.sh montclair_state_ws167c.blend $c 2>&1 | grep -E "WROTE|WATCH|rror"
done; echo "$(date +%T) ALL DONE"
