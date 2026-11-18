import bpy, os
cam_name = os.environ['CAM']
out = os.environ['OUT']
sc = bpy.context.scene
cam = bpy.data.objects.get(cam_name)
if not cam:
    raise SystemExit(f'cam not found {cam_name}')
sc.camera = cam
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 40
sc.cycles.use_denoising = True
sc.render.resolution_x = 1280
sc.render.resolution_y = 720
sc.render.resolution_percentage = 100
sc.render.filepath = out
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 90
bpy.ops.render.render(write_still=True)
print('Saved', out)
