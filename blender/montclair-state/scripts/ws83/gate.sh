#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
[ -f montclair_state_pre_20261112ws83.blend ] || cp montclair_state.blend montclair_state_pre_20261112ws83.blend
sha256sum montclair_state.blend > scripts/ws83/sha_before.txt
while :; do
 a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); now=$(date +%H%M)
 [ "$now" -ge 0628 ] && { echo "$(date +%T) GAVE UP avail=$a"; exit 1; }
 if [ "$a" -gt ${GATE:-4800} ]; then
  echo "$(date +%T) START avail=$a"
  WD_MIN=900 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws83/apply83a.py 2>&1 | grep -E "WS83a|rror|Trace|WATCHDOG"
  sha256sum montclair_state.blend | tee scripts/ws83/sha_after.txt
  cmp -s <(cut -c1-64 scripts/ws83/sha_before.txt) <(cut -c1-64 scripts/ws83/sha_after.txt) || { echo "$(date +%T) APPLIED"; break; }
  sleep 20
 else sleep 10; fi
done
SAMP=16 PCT=55 bash scripts/ws82/r.sh ws83 wip WS80_CAM_oblique_sprague_lot_SW=oblique_sprague_lot_lane_walk_band,WS80_CAM_eye_sprague_lane_from_S=eye_sprague_lane_from_S,WS81_CAM_eye_grandstand_lawn_from_SE=eye_grandstand_lawn_from_SE,WS81_CAM_closeup_lane_seam=closeup_lane_walk_edge_band
echo "$(date +%T) GATE DONE"
