import bpy, os
from mathutils import Vector
sc=bpy.context.scene
cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); sc.camera=cam
cam.data.lens=30; cam.location=(-64.6,-193.5,127.0+1.6)
d=Vector((-68.6,-184.5,127.75))-cam.location; cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
sun=bpy.data.objects.new('S',bpy.data.lights.new('S','SUN')); sun.data.energy=3; sun.rotation_euler=(0.8,0.2,2.5); sc.collection.objects.link(sun)
if not sc.world: sc.world=bpy.data.worlds.new('W')
sc.world.color=(0.5,0.55,0.6)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16; sc.render.resolution_x=768; sc.render.resolution_y=432
sc.render.filepath=os.environ['OUTP']; sc.render.image_settings.file_format='JPEG'
bpy.ops.render.render(write_still=True); print("PREV",os.environ['OUTP'])
