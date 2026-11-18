import bpy, math
from mathutils import Vector
def mk(nm,loc,tgt,lens):
    o=bpy.data.objects.get(nm)
    if not o:
        cd=bpy.data.cameras.new(nm); o=bpy.data.objects.new(nm,cd); bpy.data.collections['WG_Bohn_W_door_landing_UNVERIFIED'].objects.link(o)
    o.data.lens=lens; o.data.clip_end=30000; o.location=loc; d=Vector(tgt)-Vector(loc)
    o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2); o['wg_obj']=1
mk('WG_CAM_closeup_Bohn_W_door_landing',(209.0,399.8,137.0),(215.2,405.6,134.7),26)
bpy.ops.wm.save_mainfile(); print('SAVED')
