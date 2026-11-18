#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
log(){ echo "$(date +%T) $*"; }
applied=0; rendered=0
while [ "$(date +%H%M)" -lt 0410 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ $applied = 0 ] && [ "$a" -gt 5300 ]; then
    log "avail $a — crown rebuild"
    cp montclair_state.blend montclair_state_pre_20261111ws49.blend
    printf '#!/bin/bash\ncp /workspace/nj-scenes/montclair-state/montclair_state_pre_20261111ws49.blend /workspace/nj-scenes/montclair-state/montclair_state.blend\n' > scripts/ws49/ws49_revert_all.sh; chmod +x scripts/ws49/ws49_revert_all.sh
    out=$(SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws49/crown.py 2>&1 | grep -E "C49|rror|WATCHDOG"); echo "$out"
    echo "$out" | grep -q "C49 saved" && applied=1
    sha256sum montclair_state.blend; continue
  fi
  if [ $applied = 1 ] && [ "$a" -gt 7500 ]; then
    log "avail $a — WIP render"
    SAMP=16 PCT=55 OUT_TAG=GOLDEN_ws49_goldenhour CAMS='WS49_CAM_oblique_band_trees_SE_from_campus=oblique_band_trees_SE_from_campus,WS49_CAM_eye_band_from_Kasser_frontage=eye_band_from_Kasser_frontage,WS49_CAM_eye_band_from_CCOM_east=eye_band_from_CCOM_east,WS49_CAM_closeup_band_crowns=closeup_band_crowns' WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws49/render49.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"
    rendered=1; break
  fi
  sleep 20
done
log "gate end applied=$applied rendered=$rendered"
echo "- ws49 gate $(date '+%I:%M %p') ET: applied=$applied rendered=$rendered; see montclair-state/scripts/ws49/gate.log" >> /workspace/nj-scenes/LOG.md
rm -f /workspace/nj-scenes/.lock
