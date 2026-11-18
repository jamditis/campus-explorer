#!/usr/bin/env bash
# 2026-10-15 ax: soft light + tree variety WIP (sequential; one Blender at a time). EXR + OIDN.
set -uo pipefail
ROOT=/workspace/nj-scenes; MS=$ROOT/montclair-state; B=$ROOT/tools/blender_slot.sh; O=$MS/renders/wip
T=$(cat /tmp/ax_prefix.txt); VT=AgX; LK="AgX - Base Contrast"; DEN=$MS/scripts/denoise_exr.py
mkdir -p /tmp/ax "$O"
main_one() { local i="$1" cam="$2" th="$3" seg="$4"
  echo "=== r$i $cam"; free -m | awk '/^Mem:/{print "avail_before",$7}'
  EXR=1 EXPOSURE=0.0 TEXLIM=512 CULL=300 THREADS=2 TREE_HIDE_M="$th" TREE_HIDE_SEG_M="$seg" LOOK="$LK" \
    HIDE="grass_tiles_3g,Lawn_grass_leaves_3f,Morehead_windows_modelled,Site_furniture,Day2_details" SLOT_MIN_AVAIL_MB=1400 \
    timeout 1500 $B -b "$MS/montclair_state.blend" --python "$MS/scripts/ccom_render_batch_20261015ax.py" -- exterior /tmp/ax "${T}_" 1280 40 "$cam" >/tmp/ax/r$i.log 2>&1 || { echo "RENDER FAIL $i"; tail -20 /tmp/ax/r$i.log; return 1; }
  rg -n "TREE_HIDE|RENDERED|peakrss" /tmp/ax/r$i.log | tail -4
  SLOT_MIN_AVAIL_MB=1200 timeout 600 $B -b --factory-startup --python "$DEN" -- "/tmp/ax/${T}_${cam}.exr" "$O/${T}_${cam}_ax.jpg" "$VT" "$LK" 0.0 1280 720 >/tmp/ax/d$i.log 2>&1 || { echo "DENOISE FAIL $i"; tail -10 /tmp/ax/d$i.log; }
  ls -la "$O/${T}_${cam}_ax.jpg"; rm -f "/tmp/ax/${T}_${cam}.exr"; }
north_one() { local i="$1" cam="$2" th="$3" seg="$4"
  echo "=== r$i north $cam"; free -m | awk '/^Mem:/{print "avail_before",$7}'
  ( cd $MS/north && EXR=1 SPP=40 PCT=100 OUT=/tmp/ax/n$i.exr CAM=$cam TREE_HIDE_M=$th TREE_HIDE_SEG_M=$seg timeout 1500 $B -b montclair_north.blend --python scripts/render_north.py >/tmp/ax/r$i.log 2>&1 )
  VS=$(grep VIEWSET /tmp/ax/r$i.log | head -1); EX=$(echo "$VS" | awk -F'|' '{gsub(/^ +| +$/,"",$3); print $3}')
  echo "$VS"; EXF=$(ls /tmp/ax/n$i*.exr 2>/dev/null | head -1)
  SLOT_MIN_AVAIL_MB=1200 timeout 600 $B -b --factory-startup --python "$DEN" -- "$EXF" "$O/${T}_${cam}_ax.jpg" "$VT" "$LK" "$EX" 1280 720 >/tmp/ax/d$i.log 2>&1 || echo "DENOISE FAIL $i"
  ls -la "$O/${T}_${cam}_ax.jpg"; rm -f "$EXF"; }

main_one 2 CAM_closeup_trees_variety_ax 0 0
north_one 3 CAM_eye_richardson_promenade 0 0

echo ALL_DONE $T
