import bpy,math
from mathutils import Vector
def mkcam(name,loc,tgt,lens):
    c=bpy.data.cameras.new(name); c.lens=lens; c.sensor_width=36; o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    o.location=loc; d=Vector(tgt)-Vector(loc); o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); bpy.context.view_layer.update(); return o
mkcam('PROBECAM',(-175,-150,175),(-250,-55,124.0),30)
