#!/bin/bash
# Session ud WIP renders. Check free -m first.
set -e
B=/workspace/opt/blender/blender
BLEND=/workspace/nj-scenes/montclair-state/montclair_state.blend
PY=/workspace/nj-scenes/montclair-state/scripts/ud/ud_render_one.py
OUTDIR=/workspace/nj-scenes/montclair-state/renders/wip
TS=${TS:-$(date +%Y%m%d-%H%M)}
SPP=${SPP:-36}
RES=${RES:-1280}
mkdir -p "$OUTDIR" /workspace/nj-scenes/montclair-state/data/ud
echo "$TS" > /workspace/nj-scenes/montclair-state/data/ud/wip_ts.txt
free -m | awk '/Mem:/{print "avail_before",$7}'
cams=(
  "UD_CAM_oblique_day9_polish_from_SW:oblique_day9_polish_from_SW"
  "UA_CAM_eye_NormalAve_from_N:eye_NormalAve_from_N"
  "TY_CAM_eye_Nursing_W_walks:eye_Partridge_W_walks"
  "UD_CAM_closeup_NormalAve_asphalt:closeup_NormalAve_asphalt"
)
for pair in "${cams[@]}"; do
  IFS=: read -r CAM TAG <<< "$pair"
  OUT="$OUTDIR/${TS}_${CAM}_ud.jpg"
  # also short name alias pattern used in prior sessions: TS_CAM_ud.jpg is fine
  echo "=== $CAM ==="
  avail=$(free -m | awk '/Mem:/{print $7}')
  if [ "$avail" -lt 2000 ]; then SPP=28; RES=1024; echo "low mem $avail -> spp $SPP res $RES"; fi
  CAM="$CAM" OUT="$OUT" SPP="$SPP" RES="$RES" \
    $B -b "$BLEND" --python "$PY" \
    > /workspace/nj-scenes/montclair-state/data/ud/r_${TAG}.log 2>&1
  tail -3 /workspace/nj-scenes/montclair-state/data/ud/r_${TAG}.log
  ls -la "$OUT" || ls -la "${OUT}.jpg" || true
done
free -m | awk '/Mem:/{print "avail_after",$7}'
