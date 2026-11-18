"""Render 4 vd WIP cams 1280x720 ~40 samples denoised CPU."""
import bpy, os
from datetime import datetime
ts = datetime.now().strftime('%Y%m%d-%H%M')
open('/workspace/nj-scenes/montclair-state/data/vd/wip_ts.txt','w').write(ts)
OUT = '/workspace/nj-scenes/montclair-state/renders/wip'
os.makedirs(OUT, exist_ok=True)
cams = [
    'UY_CAM_oblique_Freeman_from_NW',
    'UV_CAM_eye_Freeman_N_entrance',
    'UY_CAM_eye_Freeman_W_side',
    'VD_CAM_closeup_Freeman_W_pane_grid',
]
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
    fp = f'{OUT}/{ts}_{name}_vd.jpg'
    sc.render.filepath = fp
    print('RENDER', name, '->', fp)
    bpy.ops.render.render(write_still=True)
    print('DONE', name, os.path.getsize(fp) if os.path.exists(fp) else 0)
print('TS', ts)
