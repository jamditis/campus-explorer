cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${NEED:-5200} ]; do
  [ $(date +%s) -ge ${END_EPOCH:-0} ] && { echo "$(date +%T) NOGO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 1; }
  sleep 10; done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup ${SRC:-montclair_state.blend} --python scripts/ws156/fix156.py 2>&1 | grep -E "FIX156|SAVED|rror|Trace|WATCH" | cut -c1-600
[ -e montclair_state_ws156a.blend ] || exit 2
echo "$(date +%T) FIX DONE avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
for c in ${CAMS156:-WS156_CAM_oblique_Freeman_N_end_from_NE=oblique_Freeman_N_end_from_NE WS156_CAM_closeup_Freeman_N_lettering=closeup_Freeman_N_lettering WS156_CAM_eye_Freeman_N_entrance_from_NE=eye_Freeman_N_entrance_from_NE WS156_CAM_eye_Freeman_N_end_from_N_lawn=eye_Freeman_N_end_from_N_lawn}; do
  until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${NEEDR:-4300} ]; do [ $(date +%s) -ge ${END_EPOCH:-0} ] && { echo "$(date +%T) RENDER NOGO $c"; break 2; }; sleep 10; done
  CULL=-170,-40,-260,-140 DIR=wip OUT_TAG=${TAG156:-ws156} bash scripts/ws148/rt.sh montclair_state_ws156a.blend $c
done
echo "$(date +%T) ALL DONE"
