#!/usr/bin/env bash
# 2026-10-15 aw CCOM WIP renders (sequential). EXR=1 + OIDN denoise.
set -euo pipefail
ROOT=/workspace/nj-scenes
MS=$ROOT/montclair-state
B=$ROOT/tools/blender_slot.sh
O=$MS/renders/wip
T=$(cat /tmp/aw_prefix.txt | cut -d= -f2)
VT=AgX
LK="AgX - Medium High Contrast"
DEN=$MS/scripts/denoise_exr.py
mkdir -p /tmp/aw "$O"

render_one() {
  local i="$1" mode="$2" cam="$3" spp="$4" expo="$5" th="$6" seg="$7" nm="$8"
  echo "=== r$i $cam mode=$mode spp=$spp expo=$expo TREE_HIDE $th/$seg ==="
  free -m | awk '/^Mem:/{print "avail_before",$7}'
  EXR=1 EXPOSURE="$expo" TEXLIM=512 CULL=300 THREADS=2 \
    TREE_HIDE_M="$th" TREE_HIDE_SEG_M="$seg" \
    HIDE="grass_tiles_3g,Lawn_grass_leaves_3f,Morehead_windows_modelled,Site_furniture,Day2_details" \
    SLOT_MIN_AVAIL_MB=1400 \
    timeout 1500 $B -b "$MS/montclair_state.blend" --python "$MS/scripts/ccom_render_batch_20261014y.py" -- \
      "$mode" /tmp/aw "${T}_" 1280 "$spp" "$cam" \
      >/tmp/aw/r$i.log 2>&1 || { echo "RENDER FAIL $i"; tail -30 /tmp/aw/r$i.log; return 1; }
  rg -n "TREE_HIDE|RENDERED|BATCH DONE|peakrss|rss" /tmp/aw/r$i.log | tail -8
  local EXF=/tmp/aw/${T}_${cam}.exr
  # batch names files as prefix+cam.exr
  EXF=/tmp/aw/${T}_${cam}.exr
  # wait — batch uses prefix+cam.ext; our prefix already has trailing _
  # Actually prefix is ${T}_ so file is /tmp/aw/${T}_CAM_....exr — cam includes CAM_
  EXF="/tmp/aw/${T}_${cam}.exr"
  ls -la "$EXF" || { echo "missing $EXF"; ls /tmp/aw/; return 1; }
  SLOT_MIN_AVAIL_MB=1200 timeout 600 $B -b --factory-startup --python "$DEN" -- \
    "$EXF" "$O/${T}_${cam}.jpg" "$VT" "$LK" "$expo" 1280 720 \
    >/tmp/aw/d$i.log 2>&1 || { echo "DENOISE FAIL $i"; tail -20 /tmp/aw/d$i.log; return 1; }
  rg -n "SIZE|DENOISED|Saved|rror" /tmp/aw/d$i.log | tail -5
  ls -la "$O/${T}_${cam}.jpg"
  # free EXR to save disk
  rm -f "$EXF"
  free -m | awk '/^Mem:/{print "avail_after",$7}'
}

# 1 oblique exterior
render_one 1 exterior CAM_oblique_CCOM_east_jf 40 0.0 0 0 CAM_oblique_CCOM_east_jf
# 2 grade eye exterior  
render_one 2 exterior CAM_eye_CCOM_grade_lab 40 0.0 40 12 CAM_eye_CCOM_grade_lab
# 3 lounge photo interior
render_one 3 interior CAM_eye_CCOM_lounge_photo_al 40 0.0 0 8 CAM_eye_CCOM_lounge_photo_al
# 4 ceiling closeup interior
render_one 4 interior CAM_closeup_CCOM_lounge_ceil_20261015aw 40 0.0 0 0 CAM_closeup_CCOM_lounge_ceil_20261015aw
# 5 lab skyline (extra) — exterior mode like am (room boxes hidden? am used exterior)
render_one 5 exterior CAM_eye_CCOM_lab_skyline 40 0.0 40 12 CAM_eye_CCOM_lab_skyline

echo ALL_DONE prefix=$T
ls -la "$O/${T}_"*.jpg
