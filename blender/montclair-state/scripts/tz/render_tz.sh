#!/bin/bash
# Render 4 TZ WIP cams. EEVEE preferred; Workbench fallback if RAM tight.
set -e
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=montclair_state.blend
TS=$(date +%Y%m%d-%H%M)
OUT=renders/wip
mkdir -p "$OUT"
free -m | head -2
CAMS=(
  TZ_CAM_oblique_CollegeHall_from_NE
  TZ_CAM_eye_CollegeHall_from_E
  TZ_CAM_eye_CollegeHall_from_N
  TZ_CAM_closeup_CollegeHall_north_addition
)
for CAM in "${CAMS[@]}"; do
  FN="${OUT}/${TS}_${CAM}_tz.jpg"
  echo "RENDER $CAM -> $FN"
  $B -b "$F" -o "//${FN%.jpg}" -F JPEG -f 1 --python-expr "
import bpy
sc=bpy.context.scene
sc.render.resolution_x=1280
sc.render.resolution_y=720
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='JPEG'
sc.render.image_settings.quality=90
# EEVEE quick
try:
    sc.render.engine='BLENDER_EEVEE_NEXT'
except:
    try: sc.render.engine='BLENDER_EEVEE'
    except: sc.render.engine='BLENDER_WORKBENCH'
if hasattr(sc,'eevee'):
    if hasattr(sc.eevee,'taa_render_samples'): sc.eevee.taa_render_samples=16
cam=bpy.data.objects.get('$CAM')
if not cam: raise SystemExit('missing cam $CAM')
sc.camera=cam
sc.render.filepath=bpy.path.abspath('//${FN%.jpg}')
bpy.ops.render.render(write_still=True)
print('WROTE', sc.render.filepath)
" 2>&1 | grep -E 'WROTE|Error|Traceback|Saved|missing' | grep -v BlenderGIS || true
  # blender -o appends frame number; normalize name
  # find newest matching
  ls -lt ${OUT}/${TS}_${CAM}* 2>/dev/null | head -3
  free -m | head -2
done
echo DONE_RENDERS
ls -la ${OUT}/${TS}_*_tz.jpg 2>/dev/null || ls -la ${OUT}/${TS}_*tz* 2>/dev/null | head
