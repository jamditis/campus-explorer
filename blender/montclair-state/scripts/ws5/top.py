import bpy,os
sc=bpy.context.scene
cd=bpy.data.cameras.new('ws5top'); cd.type='ORTHO'; cd.ortho_scale=float(os.environ.get('OS','70'))
c=bpy.data.objects.new('ws5top',cd); sc.collection.objects.link(c)
x,y=[float(v) for v in os.environ.get('XY','-105,-55').split(',')]
c.location=(x,y,175); cd.clip_start=1; cd.clip_end=80; c.rotation_euler=(0,0,0); sc.camera=c
sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.color_type='MATERIAL'; sc.display.shading.light='FLAT'
sc.render.resolution_x=1000; sc.render.resolution_y=1000; sc.render.resolution_percentage=100
sc.render.filepath=os.environ['OUT']; sc.render.image_settings.file_format='PNG'
for o in sc.objects:
  if o.type=='MESH' and ('grass' in o.name.lower() or 'Tree' in o.name or 'tree' in o.name or 'canopy' in o.name.lower()): o.hide_render=True
bpy.ops.render.render(write_still=True)
