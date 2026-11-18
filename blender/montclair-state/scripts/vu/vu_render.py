"""Render 4 vu WIP cams 1280x720 modest samples denoised CPU."""
import bpy, os
from datetime import datetime
ts = os.environ.get('FORCE_TS') or datetime.now().strftime('%Y%m%d-%H%M')
open('/workspace/nj-scenes/montclair-state/data/vu/wip_ts.txt','w').write(ts)
OUT = '/workspace/nj-scenes/montclair-state/renders/wip'
os.makedirs(OUT, exist_ok=True)
cams = [
    'TI_CAM_oblique_east_dorms_from_SW',
    'VU_CAM_closeup_Blanton_S_door_bandcut',
    'VU_CAM_eye_Blanton_W_door_bandcut',
    'TU_CAM_eye_Blanton_W_entrances',
]
only = os.environ.get('CAM')
if only:
    cams = [c for c in cams if c == only] or [only]
samples = int(os.environ.get('SAMPLES', '36'))
res_pct = int(os.environ.get('RESPCT', '90'))
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
except Exception:
    pass
# obj count
nobj = len(bpy.data.objects)
nvis = sum(1 for o in bpy.data.objects if not o.hide_render)
open('/workspace/nj-scenes/montclair-state/data/vu/obj_count.txt','w').write(f'{nobj} {nvis}\n')
print('OBJS', nobj, 'visible', nvis, flush=True)
for name in cams:
    cam = bpy.data.objects.get(name)
    if not cam:
        print('MISSING', name); continue
    sc.camera = cam
    fp = f'{OUT}/{ts}_{name}_vu.jpg'
    if os.environ.get('SKIP_EXISTING') == '1' and os.path.exists(fp):
        print('SKIP', name, fp, flush=True); continue
    sc.render.filepath = fp
    print('RENDER', name, '->', fp, 'spp', samples, 'res%', res_pct, flush=True)
    bpy.ops.render.render(write_still=True)
    print('DONE', name, os.path.getsize(fp) if os.path.exists(fp) else 0, flush=True)
print('TS', ts, flush=True)
