cd /workspace/nj-scenes/montclair-state
[ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5200 ] || { echo NOGO; exit 1; }
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws157a.blend --python scripts/ws157/fix157b.py 2>&1 | grep --line-buffered -E "FIX157|SAVED|rror|Trace|WATCH" | cut -c1-500
[ -e montclair_state_ws157b.blend ] || exit 2
for c in WS157_CAM_closeup_Freeman_N_bay_top=closeup_Freeman_N_bay_top WS156_CAM_eye_Freeman_N_entrance_from_NE=eye_Freeman_N_entrance_from_NE WS156_CAM_eye_Freeman_N_end_from_N_lawn=eye_Freeman_N_end_from_N_lawn WS156_CAM_oblique_Freeman_N_end_from_NE=oblique_Freeman_N_end_from_NE; do
  until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4300 ]; do sleep 10; done
  CULL=-170,-40,-260,-140 DIR=wip OUT_TAG=ws157b bash scripts/ws148/rt.sh montclair_state_ws157b.blend $c
done; echo "$(date +%T) ALL DONE"
