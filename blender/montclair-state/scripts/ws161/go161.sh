cd /workspace/nj-scenes/montclair-state
BASE=montclair_state_ws160b.blend; [ -e $BASE ] || BASE=montclair_state_ws160a.blend
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5200 ]; do sleep 5; done
echo "$(date +%T) GO base=$BASE"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup $BASE --python scripts/ws161/fix161.py 2>&1 | grep --line-buffered -E "FIX161|rror|Trace|WATCH" | cut -c1-400
[ -e montclair_state_ws161a.blend ] || exit 2
echo "$(date +%T) fix done"
for c in WS161_CAM_oblique_Panzer_gym_SW_from_Lot3=oblique_Panzer_gym_SW_from_Lot3 WS161_CAM_eye_Panzer_W_facade_from_Lot3_aisle=eye_Panzer_W_facade_from_Lot3_aisle WS161_CAM_eye_Panzer_S_block_from_SW=eye_Panzer_S_block_from_SW WS161_CAM_closeup_Panzer_W_door_clerestory=closeup_Panzer_W_door_clerestory WS160_CAM_oblique_Panzer_gym_roof_from_SE=oblique_Panzer_gym_roof_from_SE; do
  for try in 1 2 3; do
    until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4300 ]; do sleep 10; done
    CULL=-380,-200,-290,-120 DIR=${DIR:-wip} OUT_TAG=ws161a bash scripts/ws161/rt.sh montclair_state_ws161a.blend $c | tee /tmp/r161.txt
    grep -q WROTE /tmp/r161.txt && break
  done
done; echo "$(date +%T) ALL DONE"
