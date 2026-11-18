import bpy, math
from mathutils import Vector
cd=bpy.data.cameras.new('WM_CAM_closeup_stone_foundation_from_SW'); cd.lens=30; cd.clip_end=30000
o=bpy.data.objects.new('WM_CAM_closeup_stone_foundation_from_SW',cd)
bpy.data.objects['WA1_CAM_eye_stone_footway_from_S'].users_collection[0].objects.link(o)
o.location=(136.4,255.6,137.75); d=Vector((140.6,260.2,136.65))-o.location
o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2)
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
