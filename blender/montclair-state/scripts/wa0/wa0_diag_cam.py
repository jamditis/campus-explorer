import bpy
from mathutils import Vector
sc=bpy.context.scene
cd=bpy.data.cameras.new('tmp'); cam=bpy.data.objects.new('TMP_CAM',cd); sc.collection.objects.link(cam)
P=Vector((116.5,279.6,138.6)); T=Vector((112.6,281.2,137.75))
cam.location=P; cam.rotation_euler=(T-P).to_track_quat('-Z','Y').to_euler(); cd.lens=35; cd.clip_start=0.05
sc.camera=cam
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=60
sc.render.image_settings.file_format='JPEG'; sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.render.filepath='/workspace/nj-scenes/montclair-state/data/wa0/diag_corner_after.jpg'
bpy.ops.render.render(write_still=True); print('DONE')
