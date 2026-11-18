cd /workspace/nj-scenes/montclair-state
DEAD=$(date -d 'today 07:00' +%s)
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5200 ]; do [ $(date +%s) -ge $DEAD ] && { echo "$(date +%T) NOGO memory"; exit 1; }; sleep 10; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws157/fix157.py 2>&1 | grep --line-buffered -E "FIX157|SAVED|rror|Trace|WATCH" | cut -c1-600
[ -e montclair_state_ws157a.blend ] || exit 2
for c in WS157_CAM_closeup_Freeman_N_bay_top=closeup_Freeman_N_bay_top WS156_CAM_eye_Freeman_N_entrance_from_NE=eye_Freeman_N_entrance_from_NE WS156_CAM_eye_Freeman_N_end_from_N_lawn=eye_Freeman_N_end_from_N_lawn WS156_CAM_oblique_Freeman_N_end_from_NE=oblique_Freeman_N_end_from_NE; do
  until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4300 ]; do sleep 10; done
  CULL=-170,-40,-260,-140 DIR=wip OUT_TAG=ws157 bash scripts/ws148/rt.sh montclair_state_ws157a.blend $c
done; echo "$(date +%T) ALL DONE"
