#!/bin/bash
# ws52: per-camera culled WIP renders of the ws49 crowns, one at a time, when memory allows (to 06:40)
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
log(){ echo "$(date +%T) $*"; }
JOBS=("WS49_CAM_closeup_band_crowns=closeup_band_crowns|150,330,-330,-190"
"WS49_CAM_eye_band_from_CCOM_east=eye_band_from_CCOM_east|20,700,-650,-20"
"WS49_CAM_eye_band_from_Kasser_frontage=eye_band_from_Kasser_frontage|-720,-160,-520,-80"
"WS49_CAM_oblique_band_trees_SE_from_campus=oblique_band_trees_SE_from_campus|-40,750,-750,20")
i=0
while [ $i -lt ${#JOBS[@]} ] && [ "$(date +%H%M)" -lt 0640 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 6000 ]; then
    c=${JOBS[$i]%%|*}; cull=${JOBS[$i]##*|}
    log "avail $a — render $c"
    out=$(CULL=$cull TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=GOLDEN_ws52_goldenhour CAMS="$c" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws52/render52.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && i=$((i+1))
    continue
  fi
  sleep 20
done
log "gate end rendered=$i/4"
echo "- ws52 gate $(date '+%I:%M %p') ET: rendered $i/4 WIPs (GOLDEN_ws52); see montclair-state/scripts/ws52/gate.log" >> /workspace/nj-scenes/LOG.md
rm -f /workspace/nj-scenes/.lock
