cd /workspace/nj-scenes/montclair-state
for c in WS162_CAM_oblique_Lot3_from_W_high=oblique_Lot3_W_bank_light_from_W_high WS162_CAM_eye_Lot3_from_Sprague_walk_NW=eye_Lot3_W_bank_from_Sprague_walk_NW WS169_CAM_closeup_bank_S_end_from_SW=closeup_bank_S_end_from_SW WS167_CAM_eye_lane_N_along_bleachers_from_S=eye_lane_N_bleachers_light_from_S; do
 until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 8000 ]; do
   [ $(date +%H%M) -ge 1908 ] && { echo "$(date +%T) RENDER TIMEOUT avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 3; }; sleep 5; done
 echo "$(date +%T) R $c $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
 CAMS="$c" DIR=wip OUT_TAG=ws169a SAMP=16 PCT=60 TEXLIM=1024 CULL=-380,-260,-300,-140 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws169a.blend --python scripts/ws169/render169.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"
done; echo "$(date +%T) ALL DONE"
