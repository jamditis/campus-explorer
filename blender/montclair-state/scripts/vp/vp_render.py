"""Render 4 vo WIP cams 1280x720 modest samples denoised CPU. RES% via env."""
import bpy, os
from datetime import datetime
ts = os.environ.get('FORCE_TS') or datetime.now().strftime('%Y%m%d-%H%M')
open('/workspace/nj-scenes/montclair-state/data/vp/wip_ts.txt','w').write(ts)
OUT = '/workspace/nj-scenes/montclair-state/renders/wip'
os.makedirs(OUT, exist_ok=True)
cams = [
    'UY_CAM_oblique_Freeman_from_NW',
    'UV_CAM_eye_Freeman_N_entrance',
    'UY_CAM_eye_Freeman_W_side',
    'VP_CAM_closeup_Freeman_W_glass_grazing',
]
cs = os.environ.get('CAM_SET', '')
if cs == 'ncream':
    cams[3] = 'VP_CAM_closeup_Freeman_N_cream_punch'
elif cs == 'final':
    cams = [
        'UY_CAM_oblique_Freeman_from_NW',
        'UV_CAM_eye_Freeman_N_entrance',
        'UY_CAM_eye_Freeman_W_side',
        'VP_CAM_closeup_Freeman_W_glass_grazing',
    ]
elif cs == 'bonus':
    cams = ['VP_CAM_closeup_Freeman_N_cream_punch']
only = os.environ.get('CAM')
if only:
    cams = [c for c in cams if c == only] or [only]
samples = int(os.environ.get('SAMPLES', '40'))
res_pct = int(os.environ.get('RESPCT', '100'))
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = samples
sc.cycles.use_denoising = True
sc.render.resolution_x = 1280
sc.render.resolution_y = 720
sc.render.resolution_percentage = res_pct
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
    fp = f'{OUT}/{ts}_{name}_vp.jpg'
    if os.environ.get('SKIP_EXISTING')=='1' and os.path.exists(fp):
        print('SKIP', name, fp, flush=True); continue
    sc.render.filepath = fp
    print('RENDER', name, '->', fp, 'spp', samples, 'res%', res_pct, flush=True)
    bpy.ops.render.render(write_still=True)
    print('DONE', name, os.path.getsize(fp) if os.path.exists(fp) else 0, flush=True)
print('TS', ts, flush=True)
