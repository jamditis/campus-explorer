#!/bin/bash
set -e
B=/workspace/opt/blender/blender
BLEND=/workspace/nj-scenes/montclair-state/montclair_state.blend
OUT=/workspace/nj-scenes/montclair-state/renders/wip
LOG=/workspace/nj-scenes/montclair-state/data/ty
TS=$(date +%Y%m%d-%H%M)
CAMS=(
  TY_CAM_oblique_Nursing_approaches_from_SW
  TY_CAM_eye_Nursing_W_walks
  TY_CAM_eye_Nursing_E_walks
  TY_CAM_closeup_Nursing_W_steps
)
for CAM in "${CAMS[@]}"; do
  free -m | head -2
  FN="${TS}_${CAM}_ty"
  echo "=== RENDER $CAM -> $FN ==="
  $B -b "$BLEND" -P /dev/stdin << PY
import bpy
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.device='CPU'
sc.cycles.samples=40
sc.cycles.use_denoising=True
sc.render.resolution_x=1280
sc.render.resolution_y=720
sc.render.resolution_percentage=100
sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/wip/${FN}'
sc.render.image_settings.file_format='JPEG'
sc.render.image_settings.quality=90
cam=bpy.data.objects.get('${CAM}')
assert cam, 'missing ${CAM}'
sc.camera=cam
bpy.ops.render.render(write_still=True)
print('WROTE', sc.render.filepath)
PY
  sleep 1
  # rename with actual minute if blender added frame number
  ls -lh "$OUT/${FN}"* 2>/dev/null || ls -lh "$OUT/${TS}"*"${CAM}"* 2>/dev/null || true
done
echo DONE_RENDERS
date
