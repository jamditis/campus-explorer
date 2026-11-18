#!/usr/bin/env bash
# 2026-10-16 bf: American Beech variety + WIP (sequential). EXR + OIDN.
# 2026-10-16 bd: tulip leaf fix + CCOM detail WIP (sequential). EXR + OIDN.
set -uo pipefail
ROOT=/workspace/nj-scenes; MS=$ROOT/montclair-state; B=$ROOT/tools/blender_slot.sh; O=$MS/renders/wip
T=$(cat /tmp/bf_prefix.txt); VT=AgX; LK="AgX - Base Contrast"; DEN=$MS/scripts/denoise_exr.py
mkdir -p /tmp/bfr "$O"
main_one() { local i="$1" cam="$2" th="$3" seg="$4" expo="${5:-0.0}"
  echo "=== r$i $cam expo=$expo"; free -m | awk '/^Mem:/{print "avail_before",$7}'; date
  avail=$(free -m | awk '/^Mem:/{print $7}')
  if [ "$avail" -lt 1500 ]; then echo "LOW_MEM $avail — wait"; sleep 15; fi
  EXR=1 EXPOSURE="$expo" TEXLIM=512 CULL=300 THREADS=2 TREE_HIDE_M="$th" TREE_HIDE_SEG_M="$seg" LOOK="$LK" \
    HIDE="grass_tiles_3g,Lawn_grass_leaves_3f,Morehead_windows_modelled,Site_furniture,Day2_details" SLOT_MIN_AVAIL_MB=1400 \
    timeout 1500 $B -b "$MS/montclair_state.blend" --python "$MS/scripts/ccom_render_batch_20261015ax.py" -- exterior /tmp/bfr "${T}_" 1280 40 "$cam" >/tmp/bfr/r$i.log 2>&1 || { echo "RENDER FAIL $i"; tail -25 /tmp/bfr/r$i.log; return 1; }
  rg -n "TREE_HIDE|RENDERED|peakrss|LOOK|exposure|az_exposure" /tmp/bfr/r$i.log | tail -8
  SLOT_MIN_AVAIL_MB=1200 timeout 600 $B -b --factory-startup --python "$DEN" -- "/tmp/bfr/${T}_${cam}.exr" "$O/${T}_${cam}_bf.jpg" "$VT" "$LK" "$expo" 1280 720 >/tmp/bfr/d$i.log 2>&1 || { echo "DENOISE FAIL $i"; tail -10 /tmp/bfr/d$i.log; }
  ls -la "$O/${T}_${cam}_bf.jpg"; rm -f "/tmp/bfr/${T}_${cam}.exr"; }
north_one() { local i="$1" cam="$2" th="$3" seg="$4" expo="${5:--1.0}"
  echo "=== r$i north $cam expo=$expo"; free -m | awk '/^Mem:/{print "avail_before",$7}'; date
  ( cd $MS/north && EXR=1 SPP=40 PCT=100 EXPOSURE="$expo" OUT=/tmp/bfr/n$i.exr CAM=$cam TREE_HIDE_M=$th TREE_HIDE_SEG_M=$seg \
      timeout 1500 $B -b montclair_north.blend --python scripts/render_north.py >/tmp/bfr/r$i.log 2>&1 ) || { echo "RENDER FAIL $i"; tail -25 /tmp/bfr/r$i.log; return 1; }
  VS=$(grep VIEWSET /tmp/bfr/r$i.log | head -1); echo "$VS"
  EXF=$(ls /tmp/bfr/n$i*.exr 2>/dev/null | head -1)
  SLOT_MIN_AVAIL_MB=1200 timeout 600 $B -b --factory-startup --python "$DEN" -- "$EXF" "$O/${T}_${cam}_bf.jpg" "$VT" "$LK" "$expo" 1280 720 >/tmp/bfr/d$i.log 2>&1 || echo "DENOISE FAIL $i"
  ls -la "$O/${T}_${cam}_bf.jpg"; rm -f "$EXF"; }
ONLY="${ONLY:-1234}"
# 1 oblique (az_exposure_delta -0.2)
[[ $ONLY == *1* ]] && main_one 1 CAM_oblique_CCOM_east_jf 0 0 -0.2
# 2 eye-level CCOM grade lab
[[ $ONLY == *2* ]] && main_one 2 CAM_eye_CCOM_grade_lab 40 12 0.0
# 3 eye-level north promenade
[[ $ONLY == *3* ]] && north_one 3 CAM_eye_richardson_promenade 12 8 -1.0
# 4 close-up Tulip Poplar
[[ $ONLY == *4* ]] && main_one 4 CAM_closeup_trees_tulip_bb 0 0 0.0
echo ALL_DONE $T; date; free -m | head -2
