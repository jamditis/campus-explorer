"""Low-mem UM render: radius-cull + Cycles CPU, one cam per env CAMS."""
import bpy, os
from mathutils import Vector
sc = bpy.context.scene
cams = os.environ['CAMS'].split(','); ts = os.environ['TS']; outd = os.environ.get('OUTD', 'renders/wip')
tag = os.environ.get('TAG', 'um')
RAD = float(os.environ.get('RAD', '380')); LG = float(os.environ.get('LARGE', '280'))
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = int(os.environ.get('SAMPLES', '36')); sc.cycles.use_denoising = True
sc.render.resolution_x = int(os.environ.get('RX', '1280')); sc.render.resolution_y = int(os.environ.get('RY', '720'))
pct = int(os.environ.get('RES', '80'))
sc.render.resolution_percentage = pct
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 90
if hasattr(sc.cycles, 'use_persistent_data'):
    sc.cycles.use_persistent_data = True
for c in cams:
    cam = bpy.data.objects[c]; sc.camera = cam; cl = cam.matrix_world.translation
    nh = 0
    for o in bpy.context.scene.objects:
        if o.hide_render or o.type not in ('MESH', 'CURVES', 'POINTCLOUD', 'CURVE', 'FONT'):
            continue
        if max(o.dimensions) > LG:
            continue
        bb = [o.matrix_world @ Vector(corner) for corner in o.bound_box]
        lo = Vector((min(p.x for p in bb), min(p.y for p in bb), min(p.z for p in bb)))
        hi = Vector((max(p.x for p in bb), max(p.y for p in bb), max(p.z for p in bb)))
        q = Vector((min(max(cl.x, lo.x), hi.x), min(max(cl.y, lo.y), hi.y), min(max(cl.z, lo.z), hi.z)))
        if (q - cl).length > RAD:
            o.hide_render = True; nh += 1
    print('UM_RADCULL', c, RAD, nh, 'RES%', pct, 'SPP', sc.cycles.samples)
    sc.render.filepath = f'{outd}/{ts}_{c}_{tag}.jpg'
    bpy.ops.render.render(write_still=True)
    print('UMR saved', sc.render.filepath)
