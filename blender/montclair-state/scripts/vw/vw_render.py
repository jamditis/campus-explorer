"""Render 4 vw WIP cams — prefer EEVEE if available, else Cycles CPU modest samples."""
import bpy, os
from datetime import datetime
ts = os.environ.get('FORCE_TS') or datetime.now().strftime('%Y%m%d-%H%M')
open('/workspace/nj-scenes/montclair-state/data/vw/wip_ts.txt','w').write(ts)
OUT = '/workspace/nj-scenes/montclair-state/renders/wip'
os.makedirs(OUT, exist_ok=True)
cams = [
    'TI_CAM_oblique_east_dorms_from_SW',
    'VW_CAM_eye_Bohn_W_face',
    'VW_CAM_eye_Bohn_from_SW',
    'VW_CAM_closeup_Bohn_W_grid',
]
# fallback if VW cams missing
for alt in ('TK_CAM_eye_Bohn_from_W', 'TK_CAM_oblique_Bohn_from_SW', 'TK_CAM_closeup_Bohn_SW_corner'):
    if alt not in cams and bpy.data.objects.get(alt):
        pass
only = os.environ.get('CAM')
if only:
    cams = [c for c in cams if c == only] or [only]
samples = int(os.environ.get('SAMPLES', '28'))
res_pct = int(os.environ.get('RESPCT', '85'))
sc = bpy.context.scene
engine = os.environ.get('ENGINE', 'EEVEE')
if engine.upper() == 'EEVEE':
    # Blender 4.x: BLENDER_EEVEE_NEXT or BLENDER_EEVEE
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            sc.render.engine = eng
            break
        except Exception:
            continue
    else:
        sc.render.engine = 'CYCLES'
        sc.cycles.device = 'CPU'
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        engine = 'CYCLES_FALLBACK'
    try:
        ee = sc.eevee
        if hasattr(ee, 'taa_render_samples'):
            ee.taa_render_samples = samples
        if hasattr(ee, 'use_raytracing'):
            ee.use_raytracing = True
    except Exception:
        pass
else:
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
nobj = len(bpy.data.objects)
nvis = sum(1 for o in bpy.data.objects if not o.hide_render)
open('/workspace/nj-scenes/montclair-state/data/vw/obj_count.txt','w').write(f'{nobj} {nvis}\n')
print('OBJS', nobj, 'visible', nvis, 'TS', ts, 'ENGINE', sc.render.engine, flush=True)
for name in cams:
    cam = bpy.data.objects.get(name)
    if not cam:
        print('MISSING', name, flush=True); continue
    sc.camera = cam
    fp = f'{OUT}/{ts}_{name}_vw.jpg'
    if os.environ.get('SKIP_EXISTING') == '1' and os.path.exists(fp):
        print('SKIP', name, fp, flush=True); continue
    sc.render.filepath = fp
    print('RENDER', name, '->', fp, 'spp', samples, 'res%', res_pct, flush=True)
    bpy.ops.render.render(write_still=True)
    print('DONE', name, os.path.getsize(fp) if os.path.exists(fp) else 0, flush=True)
print('TS', ts, flush=True)
