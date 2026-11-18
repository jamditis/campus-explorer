import bpy,os
from mathutils import Vector
sc=bpy.context.scene
cx,cy,S=float(os.environ.get('CX',-290)),float(os.environ.get('CY',-40)),float(os.environ.get('S',200))
cam=bpy.data.objects.new('WS68_top',bpy.data.cameras.new('WS68_top'));sc.collection.objects.link(cam)
cam.data.type='ORTHO';cam.data.ortho_scale=S;cam.location=(cx,cy,400);cam.rotation_euler=(0,0,0);cam.data.clip_end=2000
sc.camera=cam
for o in bpy.data.objects:
    if o.name.startswith('BD_') or o.name=='Context_ground_beyond_data': o.hide_render=True
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='FLAT'; sh.color_type=os.environ.get('CT','TEXTURE')
sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.render.filepath=os.environ['OUT'];sc.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True);print('WROTE',os.environ['OUT'])
