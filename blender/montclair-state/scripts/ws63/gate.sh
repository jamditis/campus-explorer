#!/bin/bash
# ws63 render gate: before (backup, test) + 4 after WIPs; one at a time; MemAvailable>5300; to 11:40
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
log(){ echo "$(date +%T) $*"; }
C="-60,260,-220,80"
JOBS=(
"montclair_state.blend|wip|GOLDEN_ws63_goldenhour|WS63_CAM_oblique_E_band=oblique_E_band_pulled_to_DTM"
"montclair_state.blend|wip|GOLDEN_ws63_goldenhour|WS63_CAM_eye_E_band_from_W=eye_E_band_from_W"
"montclair_state.blend|wip|GOLDEN_ws63_goldenhour|WS63_CAM_eye_E_band_from_SE=eye_E_band_from_SE"
"montclair_state.blend|wip|GOLDEN_ws63_goldenhour|WS63_CAM_closeup_E_band_DTM_step=closeup_E_band_DTM_step")
i=0
while [ $i -lt ${#JOBS[@]} ] && [ "$(date +%H%M)" -lt 1140 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 5300 ]; then
    IFS='|' read f d tag cam <<< "${JOBS[$i]}"
    log "avail $a — render $cam on $f"
    out=$(DIR=$d CULL=$C TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=$tag CAMS="$cam" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b $f --python scripts/ws63/render63.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && i=$((i+1))
    echo "$out" | grep -q WATCHDOG && sleep 90
    continue
  fi
  sleep 20
done
log "gate end rendered=$i/5"
