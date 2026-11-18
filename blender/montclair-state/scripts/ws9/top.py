import bpy
sc=bpy.context.scene
cd=bpy.data.cameras.new('t'); cd.type='ORTHO'; cd.ortho_scale=90
c=bpy.data.objects.new('WS9_top',cd); sc.collection.objects.link(c)
c.location=(-100,-55,165); cd.clip_start=0.5; c.rotation_euler=(0,0,0); cd.clip_end=45
sc.camera=c
sc.render.engine='BLENDER_WORKBENCH'
sc.display.shading.light='FLAT'; sc.display.shading.color_type='MATERIAL'
sc.render.resolution_x=1000; sc.render.resolution_y=1000; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='JPEG'
sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws9/top.jpg'
bpy.ops.render.render(write_still=True)
