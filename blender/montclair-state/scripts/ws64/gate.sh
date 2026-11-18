#!/bin/bash
# ws64 gate (no lock): when MemAvailable>5500 and no main-scene blender: backup, apply Kasser-north band-to-DTM (LV5 NEAR70), then before+4 WIPs; to 13:30
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
log(){ echo "$(date +%T) $*"; }
C="-320,-140,-90,110"; applied=0
JOBS=("montclair_state_pre_20261111ws64.blend|test|BEFORE_ws64|WS64_CAM_eye_Kasser_north_from_E=eye_Kasser_north_from_E_before"
"montclair_state.blend|wip|GOLDEN_ws64_goldenhour|WS64_CAM_oblique_Kasser_north=oblique_Kasser_north_pulled_to_DTM"
"montclair_state.blend|wip|GOLDEN_ws64_goldenhour|WS64_CAM_eye_Kasser_north_from_E=eye_Kasser_north_from_E"
"montclair_state.blend|wip|GOLDEN_ws64_goldenhour|WS64_CAM_eye_Kasser_north_from_NW=eye_Kasser_north_from_NW"
"montclair_state.blend|wip|GOLDEN_ws64_goldenhour|WS64_CAM_closeup_Kasser_north_pad=closeup_Kasser_north_pad")
i=0
while [ "$(date +%H%M)" -lt 1330 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  busy=$(pgrep -f "blender -b montclair_state" >/dev/null && echo 1 || echo 0)
  if [ "$a" -gt 5500 ] && [ "$busy" = 0 ] && [ ! -f /workspace/nj-scenes/.lock -o "$(cut -d' ' -f1 /workspace/nj-scenes/.lock 2>/dev/null)" = ws64 ]; then
    if [ $applied = 0 ]; then
      [ -f montclair_state_pre_20261111ws64.blend ] || cp montclair_state.blend montclair_state_pre_20261111ws64.blend
      log "avail $a — apply64"
      out=$(SAVE=1 LV=5 NEAR=70 WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws64/apply64.py 2>&1 | grep -E "A64|V64|WATCHDOG|rror"); echo "$out"
      if echo "$out" | grep -q "A64 saved\|A64 already"; then applied=1; log "C64 saved $(sha256sum montclair_state.blend|cut -c1-16)"; echo "- ws64 gate $(date '+%I:%M %p') ET: Kasser-north band-to-DTM applied to main ($(sha256sum montclair_state.blend|cut -c1-16)); revert scripts/ws64/ws64_revert_all.sh" >> /workspace/nj-scenes/LOG.md
      else sleep 90; fi
      continue
    fi
    [ $i -ge ${#JOBS[@]} ] && break
    IFS='|' read f d tag cam <<< "${JOBS[$i]}"
    log "avail $a — render $cam on $f"
    out=$(DIR=$d CULL=$C TEXLIM=1024 SAMP=16 PCT=55 OUT_TAG=$tag CAMS="$cam" WD_MIN=1500 bash scripts/ws33/wd.sh $B -b $f --python scripts/ws64/render64.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"); echo "$out"
    echo "$out" | grep -q WROTE && i=$((i+1))
    echo "$out" | grep -q WATCHDOG && sleep 90
    continue
  fi
  sleep 20
done
log "gate end applied=$applied rendered=$i/5"
echo "- ws64 render gate (no lock) $(date '+%I:%M %p') ET: applied=$applied, rendered $i/5 (BEFORE + GOLDEN_ws64 WIPs); see montclair-state/scripts/ws64/gate.log" >> /workspace/nj-scenes/LOG.md
