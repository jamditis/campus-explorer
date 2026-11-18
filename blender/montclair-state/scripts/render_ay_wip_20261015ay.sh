#!/usr/bin/env bash
# 2026-10-15 ay: soft-balance + small-leaf honey locust WIP (sequential). EXR + OIDN.
set -uo pipefail
ROOT=/workspace/nj-scenes; MS=$ROOT/montclair-state; B=$ROOT/tools/blender_slot.sh; O=$MS/renders/wip
T=$(cat /tmp/ay_prefix.txt); VT=AgX; LK="AgX - Base Contrast"; DEN=$MS/scripts/denoise_exr.py
mkdir -p /tmp/ay "$O"
main_one() { local i="$1" cam="$2" th="$3" seg="$4" expo="${5:-0.0}"
  echo "=== r$i $cam expo=$expo"; free -m | awk '/^Mem:/{print "avail_before",$7}'; date
  EXR=1 EXPOSURE="$expo" TEXLIM=512 CULL=300 THREADS=2 TREE_HIDE_M="$th" TREE_HIDE_SEG_M="$seg" LOOK="$LK" \
    HIDE="grass_tiles_3g,Lawn_grass_leaves_3f,Morehead_windows_modelled,Site_furniture,Day2_details" SLOT_MIN_AVAIL_MB=1400 \
    timeout 1500 $B -b "$MS/montclair_state.blend" --python "$MS/scripts/ccom_render_batch_20261015ax.py" -- exterior /tmp/ay "${T}_" 1280 40 "$cam" >/tmp/ay/r$i.log 2>&1 || { echo "RENDER FAIL $i"; tail -25 /tmp/ay/r$i.log; return 1; }
  rg -n "TREE_HIDE|RENDERED|peakrss|LOOK|exposure" /tmp/ay/r$i.log | tail -6
  SLOT_MIN_AVAIL_MB=1200 timeout 600 $B -b --factory-startup --python "$DEN" -- "/tmp/ay/${T}_${cam}.exr" "$O/${T}_${cam}_ay.jpg" "$VT" "$LK" "$expo" 1280 720 >/tmp/ay/d$i.log 2>&1 || { echo "DENOISE FAIL $i"; tail -10 /tmp/ay/d$i.log; }
  ls -la "$O/${T}_${cam}_ay.jpg"; rm -f "/tmp/ay/${T}_${cam}.exr"; }
north_one() { local i="$1" cam="$2" th="$3" seg="$4" expo="${5:--1.0}"
  echo "=== r$i north $cam expo=$expo"; free -m | awk '/^Mem:/{print "avail_before",$7}'; date
  ( cd $MS/north && EXR=1 SPP=40 PCT=100 EXPOSURE="$expo" OUT=/tmp/ay/n$i.exr CAM=$cam TREE_HIDE_M=$th TREE_HIDE_SEG_M=$seg \
      timeout 1500 $B -b montclair_north.blend --python scripts/render_north.py >/tmp/ay/r$i.log 2>&1 ) || { echo "RENDER FAIL $i"; tail -25 /tmp/ay/r$i.log; return 1; }
  VS=$(grep VIEWSET /tmp/ay/r$i.log | head -1); echo "$VS"
  EXF=$(ls /tmp/ay/n$i*.exr 2>/dev/null | head -1)
  SLOT_MIN_AVAIL_MB=1200 timeout 600 $B -b --factory-startup --python "$DEN" -- "$EXF" "$O/${T}_${cam}_ay.jpg" "$VT" "$LK" "$expo" 1280 720 >/tmp/ay/d$i.log 2>&1 || echo "DENOISE FAIL $i"
  ls -la "$O/${T}_${cam}_ay.jpg"; rm -f "$EXF"; }
# 1 oblique overview (main)
main_one 1 CAM_oblique_CCOM_east_jf 0 0 0.0
# 2 white-facade check (north SC plaza) — base -1.0 + ay_exposure_delta -0.2
north_one 2 CAM_eye_student_center_plaza 12 8 -1.2
# 3 eye other side (main grade lab)
main_one 3 CAM_eye_CCOM_grade_lab 40 12 0.0
# 4 closeup honey locust leaves
main_one 4 CAM_closeup_trees_variety_ax 0 0 0.0
# optional: richardson promenade for tree variety in soft balance
north_one 5 CAM_eye_richardson_promenade 12 8 -1.0
echo ALL_DONE $T; date; free -m | head -2
