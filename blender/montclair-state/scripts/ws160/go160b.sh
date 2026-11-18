cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5200 ]; do sleep 5; done
echo "$(date +%T) GO"
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws160a.blend --python scripts/ws160/fix160b.py 2>&1 | grep --line-buffered -E "FIX160|rror|Trace|WATCH" | cut -c1-400
[ -e montclair_state_ws160b.blend ] || exit 2
echo "$(date +%T) fix done"
for c in WS160_CAM_eye_Panzer_N_walk_spur_from_College_Ave=eye_Panzer_N_walk_spur_from_College_Ave WS160_CAM_oblique_Panzer_gym_roof_from_SE=oblique_Panzer_gym_roof_from_SE WS158_CAM_eye_PanzerE_from_College_Ave_S=eye_PanzerE_from_College_Ave_S WS158_CAM_closeup_PanzerE_lobby_arches=closeup_PanzerE_lobby_arches; do
  for try in 1 2 3; do
    until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4300 ]; do sleep 10; done
    CULL=-320,-200,-270,-120 DIR=wip OUT_TAG=ws160b bash scripts/ws160/rt.sh montclair_state_ws160b.blend $c | tee /tmp/r160.txt
    grep -q WROTE /tmp/r160.txt && break
  done
done; echo "$(date +%T) ALL DONE"
