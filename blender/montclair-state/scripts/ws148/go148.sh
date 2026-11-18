cd /workspace/nj-scenes/montclair-state
M=main=montclair_state.blend
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${NEED:-5200} ]; do
  [ $(date +%H%M) -ge ${DEADLINE:-2203} ] && { echo "$(date +%T) NOGO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 1; }
  sleep 10; done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
[ -e montclair_state_pre_20261114ws148.blend ] || cp -p montclair_state.blend montclair_state_pre_20261114ws148.blend
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws148/pass148.py 2>&1 | grep -E "FIX|SAVED|rror|Trace|WATCH" | cut -c1-300
ls -la montclair_state_ws148a.blend || exit 2
echo "$(date +%T) PASS DONE avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CULL=-140,-10,-260,-120 DIR=wip OUT_TAG=ws148 bash scripts/ws148/rt.sh montclair_state_ws148a.blend WS143_CAM_eye_forecourt_from_N_aisle=eye_forecourt_from_N_aisle WS148_CAM_closeup_Lot9_E_edge_to_Skyline=closeup_Lot9_E_edge_to_Skyline WS142_CAM_eye_Lot9_stalls_from_N=eye_Lot9_stalls_from_N WS146_CAM_oblique_Lot9_high_from_SE=oblique_Lot9_high_from_SE
echo "$(date +%T) ALL DONE"
