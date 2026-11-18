"""wa0: render named cameras (ONLY=cam1,cam2) with the standard WIP settings. TAG env sets suffix/prefix."""
import bpy, os
from datetime import datetime
R='/workspace/nj-scenes/montclair-state'; sc=bpy.context.scene
ONLY=[c for c in os.environ['ONLY'].split(',') if c]; TAG=os.environ.get('TAG','wa0')
ts=datetime.now().strftime('%Y%m%d-%H%M')
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=80
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.render.threads_mode='FIXED'; sc.render.threads=4
for n in ONLY:
    sc.camera=bpy.data.objects[n]; fp=f'{R}/renders/wip/{ts}_{n}_{TAG}.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('WROTE',fp,flush=True)
