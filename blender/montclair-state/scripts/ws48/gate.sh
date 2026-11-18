#!/bin/bash
# ws48 memory-gated: apply band trees to main, then full WIP render; give up at 03:40. Holds ../.lock until done.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender
log(){ echo "$(date +%T) $*"; }
applied=0
while [ "$(date +%H%M)" -lt 0340 ]; do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 5300 ]; then
    if [ $applied = 0 ]; then
      log "avail $a — building band trees"
      cp montclair_state.blend montclair_state_pre_20261111ws48.blend
      printf '#!/bin/bash\ncp /workspace/nj-scenes/montclair-state/montclair_state_pre_20261111ws48.blend /workspace/nj-scenes/montclair-state/montclair_state.blend\n' > scripts/ws48/ws48_revert_all.sh; chmod +x scripts/ws48/ws48_revert_all.sh
      SAVE=1 WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws48/band_build.py 2>&1 | grep -E "B48|rror|WATCHDOG"
      if grep -q "" /dev/null; then :; fi
      sha256sum montclair_state.blend; applied=1; continue
    else
      log "avail $a — full WIP render"
      CULL='20,230,-170,40' SAMP=16 PCT=60 OUT_TAG=GOLDEN_ws48_goldenhour CAMS='WS47_CAM_oblique_SE_QI_patch_from_SW=oblique_SE_QI_patch_from_SW,WS47_CAM_eye_QI_patch_from_S=eye_QI_patch_from_S,WS47_CAM_eye_QI_patch_from_NW=eye_QI_patch_from_NW,WS47_CAM_closeup_QI_patch_seam=closeup_QI_patch_seam' WD_MIN=1500 bash scripts/ws33/wd.sh $B -b montclair_state.blend --python scripts/ws47/render47.py 2>&1 | grep -E "WROTE|WATCHDOG|rror"
      break
    fi
  fi
  sleep 20
done
log "gate end (applied=$applied)"
echo "- ws48 gate $(date '+%I:%M %p') ET: applied=$applied; see montclair-state/scripts/ws48/gate.log" >> /workspace/nj-scenes/LOG.md
rm -f /workspace/nj-scenes/.lock
