"""Render 4 UV Freeman cams as uw WIPs 1280x720 ~36 samples denoised."""
import bpy, os
from datetime import datetime
ts = datetime.now().strftime('%Y%m%d-%H%M')
open('/workspace/nj-scenes/montclair-state/data/uw/wip_ts.txt','w').write(ts)
OUT = '/workspace/nj-scenes/montclair-state/renders/wip'
os.makedirs(OUT, exist_ok=True)
cams = [
    'UV_CAM_oblique_Freeman_from_NE',
    'UV_CAM_eye_Freeman_N_entrance',
    'UV_CAM_eye_Freeman_E_side',
    'UV_CAM_closeup_Freeman_N_entrance_doors',
]
only = os.environ.get('CAM')
if only:
    cams = [c for c in cams if c == only] or [only]
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 36
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
    fp = f'{OUT}/{ts}_{name}_uw.jpg'
    sc.render.filepath = fp
    print('RENDER', name, '->', fp)
    bpy.ops.render.render(write_still=True)
    print('DONE', name, os.path.getsize(fp) if os.path.exists(fp) else 0)
print('TS', ts)
