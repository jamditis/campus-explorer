#!/usr/bin/env bash
# 2026-10-16 bh: Life Hall windows + trough reapply WIP on north (sequential). EXR + OIDN, AgX Base Contrast, north expo -1.0.
set -uo pipefail
ROOT=/workspace/nj-scenes; MS=$ROOT/montclair-state; B=$ROOT/tools/blender_slot.sh; O=$MS/renders/wip
T=$(cat /tmp/bh_prefix.txt); VT=AgX; LK="AgX - Base Contrast"; DEN=$MS/scripts/denoise_exr.py
mkdir -p /tmp/bhr "$O"
north_one() { local i="$1" cam="$2" th="$3" seg="$4" expo="${5:--1.0}"
  echo "=== r$i north $cam expo=$expo"; free -m | awk '/^Mem:/{print "avail_before",$7}'; date
  avail=$(free -m | awk '/^Mem:/{print $7}'); if [ "$avail" -lt 1500 ]; then echo "LOW_MEM $avail — wait"; sleep 20; fi
  ( cd $MS/north && EXR=1 SPP=40 PCT=100 EXPOSURE="$expo" OUT=/tmp/bhr/n$i.exr CAM=$cam TREE_HIDE_M=$th TREE_HIDE_SEG_M=$seg SLOT_MIN_AVAIL_MB=1400 TEXLIM=512 THREADS=2 \
      timeout 1500 $B -b montclair_north.blend --python scripts/render_north.py >/tmp/bhr/r$i.log 2>&1 ) || { echo "RENDER FAIL $i"; tail -25 /tmp/bhr/r$i.log; return 1; }
  grep -E "VIEWSET|RENDERED|hid trees|Peak|rss" /tmp/bhr/r$i.log | head -5
  # peak RSS from /usr/bin/time if present in log; else from blender
  EXF=$(ls /tmp/bhr/n$i*.exr 2>/dev/null | head -1)
  SLOT_MIN_AVAIL_MB=1200 TEXLIM=512 THREADS=2 timeout 600 $B -b --factory-startup --python "$DEN" -- "$EXF" "$O/${T}_${cam}_bh.jpg" "$VT" "$LK" "$expo" 1280 720 >/tmp/bhr/d$i.log 2>&1 || echo "DENOISE FAIL $i"
  ls -la "$O/${T}_${cam}_bh.jpg"; rm -f "$EXF"; }
ONLY="${ONLY:-1234}"
[[ $ONLY == *1* ]] && north_one 1 CAM_oblique_life_bh 0 0 -1.0
[[ $ONLY == *2* ]] && north_one 2 CAM_eye_life_west_bh 12 6 -1.0
[[ $ONLY == *3* ]] && north_one 3 CAM_eye_life_south_bh 12 6 -1.0
[[ $ONLY == *4* ]] && north_one 4 CAM_closeup_life_wallbase_bh 15 0 -1.0
echo ALL_DONE $T; date; free -m | head -2
