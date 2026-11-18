cd /workspace/nj-scenes/montclair-state
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 7500 ]; do
  [ $(date +%H%M) -ge 2002 ] && { echo "$(date +%T) GATE TIMEOUT avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 3; }
  sleep 10; done
bash scripts/ws170/loop170.sh
[ -e montclair_state_ws170a.blend ] && echo "$(date +%T) FIXDONE"
for c in WS163_CAM_oblique_NormalAve_W_LotS_from_SW=oblique_NormalAve_W_utility_line_from_SW WS163_CAM_eye_NormalAve_W_from_E_walk=eye_NormalAve_W_poles_from_E_walk WS165_CAM_eye_aisle_mouth_tree_from_Normal_Ave_SE=eye_aisle_mouth_LotS_from_NormalAve_SE WS169_CAM_closeup_bank_S_end_from_SW=closeup_Lot3_S_end_from_SW; do
 until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 8000 ]; do
   [ $(date +%H%M) -ge 2016 ] && { echo "$(date +%T) RENDER TIMEOUT"; exit 3; }; sleep 5; done
 echo "$(date +%T) R $c"
 CAMS="$c" DIR=wip OUT_TAG=ws170a SAMP=16 PCT=60 TEXLIM=1024 CULL=-380,-240,-300,-140 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws170a.blend --python scripts/ws169/render169.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"
done; echo "$(date +%T) ALL DONE"
