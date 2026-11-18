cd /workspace/nj-scenes/montclair-state
[ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5200 ] || { echo NOGO; exit 1; }
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws156a.blend --python scripts/ws156/fix156b.py 2>&1 | grep -E "FIX156|SAVED|rror|Trace|WATCH" | cut -c1-400
[ -e montclair_state_ws156b.blend ] || exit 2
for c in WS156_CAM_closeup_Freeman_N_lettering=closeup_Freeman_N_lettering WS156_CAM_eye_Freeman_N_entrance_from_NE=eye_Freeman_N_entrance_from_NE WS156_CAM_eye_Freeman_N_end_from_N_lawn=eye_Freeman_N_end_from_N_lawn; do
  until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4300 ]; do sleep 10; done
  CULL=-170,-40,-260,-140 DIR=wip OUT_TAG=ws156b bash scripts/ws148/rt.sh montclair_state_ws156b.blend $c
done; echo "$(date +%T) ALL DONE"
