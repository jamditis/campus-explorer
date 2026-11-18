#!/usr/bin/env bash
# 2026-10-16 bo: CCOM OSM mid-rise band WIP on main (sequential). EXR+OIDN, AgX Base Contrast.
set -uo pipefail
ROOT=/workspace/nj-scenes; MS=$ROOT/montclair-state; B=$ROOT/tools/blender_slot.sh; O=${OUTDIR:-$MS/renders/wip}
T=$(cat /tmp/bo_prefix.txt); VT=AgX; LK="AgX - Base Contrast"; DEN=$MS/scripts/denoise_exr.py
BATCH=$MS/scripts/ccom_render_batch_20261015ax.py
mkdir -p /tmp/blr "$O"

render_one() {
  local i="$1" mode="$2" cam="$3" spp="$4" expo="$5" th="$6" seg="$7"
  echo "=== r$i $cam mode=$mode spp=$spp expo=$expo TREE_HIDE $th/$seg ==="
  free -m | awk '/^Mem:/{print "avail_before",$7}'; date
  avail=$(free -m | awk '/^Mem:/{print $7}'); if [ "$avail" -lt 1500 ]; then echo "LOW_MEM $avail — wait"; sleep 25; fi
  LOOK="$LK" EXR=1 EXPOSURE="$expo" TEXLIM=512 CULL=300 THREADS=2 \
    TREE_HIDE_M="$th" TREE_HIDE_SEG_M="$seg" \
    HIDE="grass_tiles_3g,Lawn_grass_leaves_3f,Morehead_windows_modelled,Site_furniture,Day2_details" \
    SLOT_MIN_AVAIL_MB=1400 \
    timeout 1500 $B -b "$MS/montclair_state.blend" --python "$BATCH" -- \
      "$mode" /tmp/blr "${T}_" ${RES:-1280} "$spp" "$cam" \
      >/tmp/blr/r$i.log 2>&1 || { echo "RENDER FAIL $i"; tail -30 /tmp/blr/r$i.log; return 1; }
  rg -n "TREE_HIDE|RENDERED|BATCH DONE|peakrss|rss|VIEWSET|LOOK" /tmp/blr/r$i.log | tail -10
  local EXF="/tmp/blr/${T}_${cam}.exr"
  ls -la "$EXF" || { echo "missing $EXF"; ls /tmp/blr/; return 1; }
  SLOT_MIN_AVAIL_MB=1200 TEXLIM=512 THREADS=2 timeout 600 $B -b --factory-startup --python "$DEN" -- \
    "$EXF" "$O/${T}_${cam}_bo.jpg" "$VT" "$LK" "$expo" ${RES:-1280} $(( ${RES:-1280} * 9 / 16 )) \
    >/tmp/blr/d$i.log 2>&1 || { echo "DENOISE FAIL $i"; tail -20 /tmp/blr/d$i.log; return 1; }
  ls -la "$O/${T}_${cam}_bo.jpg"
  rm -f "$EXF"
  free -m | awk '/^Mem:/{print "avail_after",$7}'
}


ONLY="${ONLY:-12345}"
[[ $ONLY == *1* ]] && render_one 1 exterior CAM_oblique_CCOM_east_jf ${SPP:-40} 0.0 0 0
[[ $ONLY == *2* ]] && render_one 2 exterior CAM_eye_CCOM_grade_lab ${SPP:-40} 0.0 40 12
[[ $ONLY == *3* ]] && render_one 3 exterior CAM_eye_CCOM_entrance ${SPP:-40} 0.0 0 0
[[ $ONLY == *4* ]] && render_one 4 exterior CAM_closeup_CCOM_lab_skyline_bm ${SPP:-40} 0.0 40 12
[[ $ONLY == *5* ]] && render_one 5 exterior CAM_eye_CCOM_lab_skyline ${SPP:-40} 0.0 40 12
echo ALL_DONE $T; date; free -m | head -2
ls -la "$O/${T}_"*_bo.jpg 2>/dev/null
