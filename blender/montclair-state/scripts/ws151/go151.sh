cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${NEED:-5200} ]; do
  [ $(date +%s) -ge ${END_EPOCH:-0} ] && { echo "$(date +%T) NOGO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 1; }
  sleep 10; done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
[ -e montclair_state_pre_20261115ws151.blend ] || cp -p montclair_state.blend montclair_state_pre_20261115ws151.blend
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws151/pass151.py 2>&1 | grep -E "FIX|LIMB149_(SWAP|VAR)|SAVED|rror|Trace|WATCH" | cut -c1-300
B=montclair_state_ws151b.blend; [ -e $B ] || B=montclair_state_ws151a.blend; [ -e $B ] || exit 2
echo "$(date +%T) PASS DONE use $B avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
for c in WS148_CAM_closeup_Lot9_E_edge_to_Skyline=closeup_Lot9_E_edge_to_Skyline WS146_CAM_oblique_Lot9_high_from_SE=oblique_Lot9_high_from_SE WS143_CAM_eye_forecourt_from_N_aisle=eye_forecourt_from_N_aisle WS142_CAM_eye_Lot9_from_Skyline_Way=eye_Lot9_from_Skyline_Way; do
  until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${NEEDR:-4300} ]; do [ $(date +%s) -ge ${END_EPOCH:-0} ] && { echo "$(date +%T) RENDER NOGO $c"; break 2; }; sleep 10; done
  CULL=-140,-10,-260,-120 DIR=wip OUT_TAG=ws151 bash scripts/ws148/rt.sh $B $c
done
echo "$(date +%T) ALL DONE"
