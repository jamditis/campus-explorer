import bpy, os
sc = bpy.context.scene
cams = os.environ['CAMS'].split(','); ts = os.environ['TS']; outd = os.environ.get('OUTD', 'renders/wip')
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = int(os.environ.get('SAMPLES', '40')); sc.cycles.use_denoising = True
sc.render.resolution_x = int(os.environ.get('RX', '1280')); sc.render.resolution_y = int(os.environ.get('RY', '720'))
sc.render.resolution_percentage = 100; sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 90
# persistent data if available
if hasattr(sc.cycles, 'use_persistent_data'):
    sc.cycles.use_persistent_data = True
for c in cams:
    sc.camera = bpy.data.objects[c]
    sc.render.filepath = f'{outd}/{ts}_{c}_uh.jpg'
    bpy.ops.render.render(write_still=True); print('UHR saved', sc.render.filepath)
