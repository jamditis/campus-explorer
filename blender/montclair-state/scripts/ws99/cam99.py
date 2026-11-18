import bpy, os
from mathutils import Vector
sc=bpy.context.scene
cd=bpy.data.cameras.new('WS99_CAM_closeup_padS_bed'); cam=bpy.data.objects.new('WS99_CAM_closeup_padS_bed',cd)
sc.collection.objects.link(cam)
cam.location=(-204.8,-96.2,129.9); d=Vector((-211.5,-90.2,127.3))-cam.location
cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); cd.lens=24; cd.clip_start=0.1
bpy.ops.wm.save_mainfile(); print('C99 saved')
