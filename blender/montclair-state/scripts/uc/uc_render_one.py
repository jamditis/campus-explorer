import bpy, os
cam=os.environ['CAM']; out=os.environ['OUT']
res=int(os.environ.get('RES','1280')); spp=int(os.environ.get('SPP','36'))
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.device='CPU'
sc.render.resolution_x=res; sc.render.resolution_y=int(res*720/1280)
sc.render.resolution_percentage=100
sc.cycles.samples=spp; sc.cycles.use_denoising=True
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.render.filepath=out if out.endswith('.jpg') else out+'.jpg'
sc.render.use_file_extension=True
sc.camera=bpy.data.objects[cam]
print('RENDER', cam, '->', sc.render.filepath, 'spp', spp)
bpy.ops.render.render(write_still=True)
print('DONE', sc.render.filepath)
