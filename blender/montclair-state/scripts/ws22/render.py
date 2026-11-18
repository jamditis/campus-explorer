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

import sys; sys.path.insert(0,R+'/scripts/ws5'); import cams; cams.CAMS.update({'WS22_CAM_closeup_Life_N_court':((34,124,139.4),(28,112,137.1),30),'WS20_CAM_closeup_Life_N_upper_windows':((31,113,140.2),(27.5,103.2,143.6),35),'WS20_CAM_oblique_Life_E_from_SE':((88,30,162),(51,62,142),30),'WS20_CAM_eye_Life_N_face':((33.9,121.8,138.6),(28.9,102.5,143.3),26),'WS20_CAM_eye_CCOM_W_face':((-39.5,8.6,138.4),(-20.0,3.9,144.5),26),'WS20_CAM_eye_CCOM_E_face_from_S':((26.9,-24.2,136.1),(31.0,-4.7,144.0),26),'WS19_CAM_tight_Morehead_SW_corner':((-52,-77,141.5),(-43.3,-68.3,143.8),55),'WS19_CAM_eye_CCOM_S_face':((2,-52,136.6),(4,-25,141.5),28),'WS19_CAM_eye_Life_W_face':((-28,60,136.6),(0,52,142),28),'WS19_CAM_closeup_Morehead_SW_hip':((-56,-82,140.5),(-42,-69,144.2),35),'WS10_CAM_oblique_cole_morehead_walk_from_S':((-60,-92,168),(-64,-54,135),26),'WS10_CAM_eye_walk_from_sign_E':((-80.5,-57.6,136.5),(-50,-54,135.6),28),'WS11_CAM_eye_cole_bed_from_SE':((-74,-82,136.6),(-90,-62,135.3),28),'WS11_CAM_closeup_trimmed_walk_end':((-79,-73,138.2),(-87,-64,135.2),30),'WS12_CAM_closeup_bridge_from_SE':((-68,-75,139.5),(-76,-66.5,134.6),30),'WS12_CAM_top_bridge':((-75,-67.5,150),(-75,-67.49,134.5),40),'WS13_CAM_eye_walk_through_bed_looking_W':((-68.6,-68.9,136.15),(-84.5,-64.4,135.0),28),'WS14_CAM_closeup_addition_east_windows':((-86.5,-79.5,136.6),(-95.6,-73.0,137.6),30),'WS14_CAM_oblique_addition_east_from_SE':((-70,-95,152),(-95,-72,138),26),'WS16_CAM_closeup_addition_eave_from_E':((-80,-68,146.5),(-93.5,-75,143.2),32)}); cams.ensure(sc)
for ONLY,LABEL in [x.split('=') for x in os.environ['CAMS'].split(',')]:
    cam = bpy.data.objects.get(ONLY)
    assert cam and cam.type == 'CAMERA', f'missing camera {ONLY}'
    sc.camera = cam
    print('CAM', ONLY, 'loc', [round(v, 2) for v in cam.matrix_world.translation], 'lens', getattr(cam.data, 'lens', None), flush=True)
    
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = int(os.environ.get('SAMP','24'))
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
