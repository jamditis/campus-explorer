"""Render ONE camera under GOLDEN lighting. Does NOT save the blend.
Env: ONLY=camera_name  OUT_TAG=goldenhour (suffix)  optional LABEL=short_name for filename.
Applies wp2 LIGHTING_PRESETS GOLDEN, renders JPEG, restores DEFAULT in-memory only (no save).
"""
import bpy, os, sys
from datetime import datetime
R = '/workspace/nj-scenes/montclair-state'
sc = bpy.context.scene
TAG = os.environ.get('OUT_TAG', 'goldenhour')
ts = datetime.now().strftime('%Y%m%d-%H%M')

# Apply GOLDEN via the same apply helper as LIGHTING_PRESETS.py
os.environ['WP2_PRESET'] = 'GOLDEN'
sys.path.insert(0, f'{R}/scripts/wp2')
# inline apply (avoid import side effects of module-level apply)
PRESET = 'GOLDEN'
p = PRESET
suns = {k: bpy.data.objects.get('WP2_Sun_' + k) for k in ('MORNING', 'GOLDEN', 'OVERCAST')}
base = bpy.data.objects.get('Sun') or bpy.data.objects.get('North_sun')
bw = bpy.data.worlds.get('Sky') or bpy.data.worlds.get('North_sky')
assert bpy.data.worlds.get('WP2_World_GOLDEN'), 'WP2_World_GOLDEN missing — lighting presets not in file'
sc.world = bpy.data.worlds['WP2_World_GOLDEN']
if base:
    base.hide_render = True
    base.hide_viewport = True
for k, o in suns.items():
    if o:
        o.hide_render = (k != p)
        o.hide_viewport = (k != p)
sc['wp2_lighting_preset'] = p
print('LIGHTING PRESET', p, sc.world.name, flush=True)

import sys; sys.path.insert(0,R+'/scripts/ws5'); import cams; cams.CAMS.update({'WS10_CAM_oblique_cole_morehead_walk_from_N':((-58,-28,157),(-64,-56,135),30),'WS10_CAM_oblique_cole_morehead_walk_from_S':((-60,-92,168),(-64,-54,135),26),'WS10_CAM_eye_walk_from_Morehead_W':((-47,-55.6,136.5),(-80,-55,135.4),28),'WS10_CAM_eye_walk_from_sign_E':((-80.5,-57.6,136.5),(-50,-54,135.6),28),'WS10_CAM_closeup_brick_edging_mid':((-63.5,-57.8,135.9),(-70,-54.6,134.8),30)}); cams.ensure(sc)
for ONLY,LABEL in [x.split('=') for x in os.environ['CAMS'].split(',')]:
    cam = bpy.data.objects.get(ONLY)
    assert cam and cam.type == 'CAMERA', f'missing camera {ONLY}'
    sc.camera = cam
    print('CAM', ONLY, 'loc', [round(v, 2) for v in cam.matrix_world.translation], 'lens', getattr(cam.data, 'lens', None), flush=True)
    
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 1280
    sc.render.resolution_y = 720
    sc.render.resolution_percentage = 80
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 90
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = 4
    
    fp = f'{R}/renders/wip/{ts}_{LABEL}_{TAG}.jpg'
    sc.render.filepath = fp
    bpy.ops.render.render(write_still=True)
    print('WROTE', fp, flush=True)
    
print('DONE NOSAVE')
