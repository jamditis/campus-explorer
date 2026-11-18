"""Render 4 vg WIP cams 1280x720 ~40 samples denoised CPU."""
import bpy, os
from datetime import datetime
ts = datetime.now().strftime('%Y%m%d-%H%M')
open('/workspace/nj-scenes/montclair-state/data/vg/wip_ts.txt','w').write(ts)
OUT = '/workspace/nj-scenes/montclair-state/renders/wip'
os.makedirs(OUT, exist_ok=True)
cams = [
    'UY_CAM_oblique_Freeman_from_NW',
    'UV_CAM_eye_Freeman_N_entrance',
    'VG_CAM_eye_Freeman_E_pane_grid',
    'VG_CAM_closeup_Freeman_S_pane_grid',
]
cs = os.environ.get('CAM_SET', '')
if cs == 'ncream':
    cams[3] = 'VG_CAM_closeup_Freeman_E_pane_grid'
elif cs in ('seob', 'final'):
    cams = [
        'VG_CAM_oblique_Freeman_from_SE',
        'UV_CAM_eye_Freeman_N_entrance',
        'VG_CAM_eye_Freeman_E_pane_grid',
        'VG_CAM_closeup_Freeman_S_pane_grid',
    ]
elif cs == 'eclose':
    cams[3] = 'VG_CAM_closeup_Freeman_E_pane_grid'
only = os.environ.get('CAM')
if only:
    cams = [c for c in cams if c == only] or [only]
samples = int(os.environ.get('SAMPLES', '40'))
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = samples
sc.cycles.use_denoising = True
sc.render.resolution_x = 1280
sc.render.resolution_y = 720
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 90
try:
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = 4
except Exception: pass
for name in cams:
    cam = bpy.data.objects.get(name)
    if not cam:
        print('MISSING', name); continue
    sc.camera = cam
    fp = f'{OUT}/{ts}_{name}_vg.jpg'
    sc.render.filepath = fp
    print('RENDER', name, '->', fp, flush=True)
    bpy.ops.render.render(write_still=True)
    print('DONE', name, os.path.getsize(fp) if os.path.exists(fp) else 0, flush=True)
print('TS', ts, flush=True)
