"""wq renders: Cycles CPU 24 spp 80%. CAMS env comma list."""
import bpy, os, math
from mathutils import Vector
from datetime import datetime
ts = os.environ.get('FORCE_TS') or datetime.now().strftime('%Y%m%d-%H%M')
OUT = os.environ.get('OUTDIR', '/workspace/nj-scenes/montclair-state/renders/wip')
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
cams = [c for c in os.environ.get('CAMS', '').split(',') if c]
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = int(os.environ.get('SAMPLES', '24'))
sc.cycles.use_denoising = True
sc.render.resolution_x = 1280
sc.render.resolution_y = 720
sc.render.resolution_percentage = int(os.environ.get('RESPCT', '80'))
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 90
sc.render.threads_mode = 'FIXED'
sc.render.threads = 4
print('OBJS', len(bpy.data.objects), 'TS', ts, flush=True)
suf = os.environ.get('SUFFIX', 'wq')
for name in cams:
    cam = bpy.data.objects.get(name)
    if not cam:
        print('MISSING', name, flush=True)
        continue
    sc.camera = cam
    fp = f'{OUT}/{ts}_{name}_{suf}.jpg'
    sc.render.filepath = fp
    bpy.ops.render.render(write_still=True)
    print('DONE', name, fp, flush=True)
