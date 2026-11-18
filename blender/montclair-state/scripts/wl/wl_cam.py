import bpy, math
from mathutils import Vector
sc=bpy.context.scene; n='WL_CAM_closeup_lawn_beside_stone_footway_from_NE'
if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
cd=bpy.data.cameras.new(n); cd.lens=32; cd.clip_end=30000
o=bpy.data.objects.new(n,cd); sc.collection.objects.link(o)
p=Vector((136.6,293.8,137.45)); t=Vector((133.6,289.2,136.45)); o.location=p; d=t-p
o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2)
print('OBJS',len(bpy.data.objects)); bpy.ops.wm.save_mainfile(); print('SAVED')
