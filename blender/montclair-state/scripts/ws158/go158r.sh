cd /workspace/nj-scenes/montclair-state
B=${1:-montclair_state_ws158a.blend}; T=${2:-ws158a}; D=${3:-test}
for c in WS158_CAM_closeup_PanzerE_lobby_arches=closeup_PanzerE_lobby_arches WS158_CAM_eye_PanzerE_from_College_Ave_S=eye_PanzerE_from_College_Ave_S WS158_CAM_eye_PanzerE_from_plaza_NE=eye_PanzerE_from_plaza_NE WS158_CAM_oblique_PanzerE_from_NE=oblique_PanzerE_from_NE; do
  until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 4300 ]; do sleep 10; done
  CULL=-330,-180,-280,-100 DIR=$D OUT_TAG=$T bash scripts/ws158/rt.sh $B $c
done; echo "$(date +%T) ALL DONE"
