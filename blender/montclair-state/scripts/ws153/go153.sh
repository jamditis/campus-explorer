cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${NEED:-5200} ]; do
  [ $(date +%s) -ge ${END_EPOCH:-0} ] && { echo "$(date +%T) NOGO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 1; }
  sleep 10; done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws152f.blend --python scripts/ws153/fix153.py 2>&1 | grep -E "FIX153|SAVED|rror|Trace|WATCH" | cut -c1-400
[ -e montclair_state_ws153a.blend ] || exit 2
echo "$(date +%T) FIX DONE avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
for c in WS152_CAM_closeup_Freeman_W_bay=closeup_Freeman_W_bay WS152_CAM_eye_Freeman_W_facade_2019match=eye_Freeman_W_facade_2019match WS142_CAM_eye_Lot9_from_Skyline_Way=eye_Lot9_E_facade_from_Skyline_Way WS152_CAM_oblique_Freeman_from_SW=oblique_Freeman_from_SW; do
  until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${NEEDR:-4300} ]; do [ $(date +%s) -ge ${END_EPOCH:-0} ] && { echo "$(date +%T) RENDER NOGO $c"; break 2; }; sleep 10; done
  CULL=-170,-40,-260,-140 DIR=wip OUT_TAG=ws153 bash scripts/ws148/rt.sh montclair_state_ws153a.blend $c
done
echo "$(date +%T) ALL DONE"
