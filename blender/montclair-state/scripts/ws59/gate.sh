#!/bin/bash
# ws59 render-only gate (no lock): autumn woods + road-end WIPs; one at a time; MemAvailable>5300; skip if main open; to 11:00
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
log(){ echo "$(date +%T) $*"; }
JOBS=("WS49_CAM_oblique_band_trees_SE_from_campus=oblique_autumn_woods_SE_from_campus|-40,750,-750,20"
"WS59_CAM_eye_woods_from_CCOM_lawn_SE=eye_autumn_woods_from_CCOM_lawn_SE|0,700,-650,-40"
"WS49_CAM_eye_band_from_Kasser_frontage=eye_autumn_woods_from_Kasser_frontage|-720,-160,-520,-80"
"WS59_CAM_closeup_road_end_cut_from_W=closeup_road_end_cut_from_W|40,160,-70,50")
i=0
while [ $i -lt ${#JOBS[@]} ] && [ "$(date +%H%M)" -lt 1100 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 5300 ] && ! pgrep -f "blender -b montclair_state.blend" >/dev/null; then
    c=${JOBS[$i]%%|*}; cull=${JOBS[$i]##*|}
    log "avail $a — render $c"
    out=$(CULL=$cull TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=GOLDEN_ws59_goldenhour CAMS="$c" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws59/render59.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && i=$((i+1))
    echo "$out" | grep -q WATCHDOG && sleep 90
    continue
  fi
  sleep 20
done
log "gate end rendered=$i/4"
echo "- ws59 render gate (no lock) $(date '+%I:%M %p') ET: rendered $i/4 GOLDEN_ws59 WIPs; see montclair-state/scripts/ws59/gate.log" >> /workspace/nj-scenes/LOG.md
