#!/bin/bash
# Render 4 UA WIP cameras. One Blender at a time. Check free mem first.
set -e
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
BLEND=${BLEND:-montclair_state.blend}
RES=${RES:-1280}
SPP=${SPP:-40}
MIN_AVAIL=${MIN_AVAIL:-1500}
TS=$(date +%Y%m%d-%H%M)
OUTDIR=renders/wip
mkdir -p "$OUTDIR" data/ua

avail=$(free -m | awk 'NR==2{print $7}')
echo "avail_mb=$avail need>=$MIN_AVAIL"
if [ "$avail" -lt "$MIN_AVAIL" ]; then
  echo "LOW MEM — dropping RES/SPP"; RES=960; SPP=24
fi

CAMS=(
  UA_CAM_oblique_NormalAve_from_SW
  UA_CAM_eye_NormalAve_from_N
  UA_CAM_eye_CollegeAve_spur_to_Normal
  UA_CAM_closeup_NormalAve_N_sidewalk
)

for CAM in "${CAMS[@]}"; do
  avail=$(free -m | awk 'NR==2{print $7}')
  echo "=== $CAM avail=$avail ==="
  if [ "$avail" -lt 1200 ]; then echo "ABORT low mem"; exit 1; fi
  OUT="$OUTDIR/${TS}_${CAM}_ua.jpg"
  $B -b "$BLEND" -o "//${OUT%.jpg}" -F JPEG -x 1 -f 1 \
    --python-expr "
import bpy
sc=bpy.context.scene
sc.render.resolution_x=$RES; sc.render.resolution_y=int($RES*720/1280)
sc.render.resolution_percentage=100
sc.cycles.samples=$SPP
sc.cycles.use_denoising=True
sc.render.image_settings.file_format='JPEG'
sc.render.image_settings.quality=90
sc.camera=bpy.data.objects['$CAM']
# light radius cull helpers if present
print('CAM', sc.camera.name, 'spp', $SPP, 'res', sc.render.resolution_x)
" 2>data/ua/r_${TS}_${CAM}.log | tee -a data/ua/render_ua.log | tail -5
  # Blender -o path is weird with //; also try explicit write
  # Re-render with freestyle-free simple script if file missing
  if [ ! -f "${OUT}" ] && [ ! -f "${OUT%.jpg}0001.jpg" ]; then
    echo "fallback render for $CAM"
    CAM="$CAM" OUT="$OUT" RES=$RES SPP=$SPP $B -b "$BLEND" --python scripts/ua/ua_render_one.py 2>>data/ua/r_${TS}_${CAM}.log | tee -a data/ua/render_ua.log | tail -8
  else
    # normalize name
    if [ -f "${OUT%.jpg}0001.jpg" ]; then mv -f "${OUT%.jpg}0001.jpg" "$OUT"; fi
  fi
  ls -la "$OUT" 2>/dev/null || ls -la renders/wip/${TS}_*ua* 2>/dev/null | tail -5
done
echo DONE
ls -la renders/wip/${TS}_*_ua.jpg 2>/dev/null
