import bpy,math
from mathutils import Vector
sc=bpy.context.scene
def mk(name,loc,tgt,lens):
    o=bpy.data.objects.get(name)
    if not o:
        cd=bpy.data.cameras.new(name); cd.clip_end=30000; o=bpy.data.objects.new(name,cd)
        col=bpy.data.objects['WA2_CAM_oblique_richardson_west_walks_from_SW'].users_collection[0]; col.objects.link(o)
    o.data.lens=lens; o.location=loc; d=Vector(tgt)-Vector(loc)
    o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2)
mk('WH_CAM_closeup_436_west_bend_from_SW',(58.8,303.8,139.55),(63.8,308.4,137.9),32)
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
