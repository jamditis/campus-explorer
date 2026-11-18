import bpy,os,sys
exec(open('render.py').read().split("import sys; sys.path.insert(0,R+'/scripts/ws5')")[0])
sc=bpy.context.scene
cam=bpy.data.objects.new('WS15_tmp_top',bpy.data.cameras.new('WS15_tmp_top')); sc.collection.objects.link(cam)
cam.data.type='ORTHO'; cam.data.ortho_scale=40; cam.location=(-95,-86,200)
sc.camera=cam
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=8; sc.cycles.use_denoising=True
sc.render.resolution_x=800; sc.render.resolution_y=800; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='JPEG'; sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/wip/ws15_probe_top_junction.jpg'
bpy.ops.render.render(write_still=True); print('WROTE')
