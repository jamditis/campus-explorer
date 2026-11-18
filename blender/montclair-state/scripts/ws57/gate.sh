#!/bin/bash
# ws57: render-only gate (no lock): ws57 pavement-lift WIPs, then the pending ws49 crown WIPs; one at a time, MemAvailable>6000, skip while any Blender has main open; to 10:30
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
log(){ echo "$(date +%T) $*"; }
JOBS=("R57|WS57_CAM_closeup_road_edge_100_m10=closeup_road_edge_lift|40,160,-70,50"
"R57|WS57_CAM_eye_footpath_from_SW=eye_footpath_lift_from_SW|0,120,-140,-20"
"R57|WS57_CAM_eye_footpath_from_NE=eye_footpath_lift_from_NE|0,120,-140,-20"
"R57|WS57_CAM_oblique_pokes_from_SW=oblique_pokes_from_SW|-60,200,-200,60"
"R52|WS49_CAM_closeup_band_crowns=closeup_band_crowns|150,330,-330,-190"
"R52|WS49_CAM_eye_band_from_CCOM_east=eye_band_from_CCOM_east|20,700,-650,-20"
"R52|WS49_CAM_eye_band_from_Kasser_frontage=eye_band_from_Kasser_frontage|-720,-160,-520,-80"
"R52|WS49_CAM_oblique_band_trees_SE_from_campus=oblique_band_trees_SE_from_campus|-40,750,-750,20")
i=0
while [ $i -lt ${#JOBS[@]} ] && [ "$(date +%H%M)" -lt 1030 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 5300 ] && ! pgrep -f "blender -b montclair_state.blend" >/dev/null; then
    j=${JOBS[$i]}; k=${j%%|*}; r=${j#*|}; c=${r%%|*}; cull=${r##*|}
    [ $k = R57 ] && S=scripts/ws57/render57.py && T=GOLDEN_ws57_goldenhour || { S=scripts/ws52/render52.py; T=GOLDEN_ws55_goldenhour; }
    log "avail $a — render $c"
    out=$(CULL=$cull TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=$T CAMS="$c" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python $S 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && i=$((i+1))
    echo "$out" | grep -q WATCHDOG && sleep 120
    continue
  fi
  sleep 20
done
log "gate end rendered=$i/8"
echo "- ws57 render gate (no lock) $(date '+%I:%M %p') ET: rendered $i/8 (first 4 = GOLDEN_ws57 lift WIPs, then GOLDEN_ws55 crown WIPs); see montclair-state/scripts/ws57/gate.log" >> /workspace/nj-scenes/LOG.md
