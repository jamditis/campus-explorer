import bpy,math,sys
from mathutils import Vector
sc=bpy.context.scene; n='WK_CAM_closeup_stone_footway_west_edge_from_SW'
o=bpy.data.objects.get(n)
if not o:
    cd=bpy.data.cameras.new(n); cd.lens=28; cd.clip_end=30000; o=bpy.data.objects.new(n,cd)
    col=bpy.data.objects['WA1_CAM_oblique_stone_footway_from_W'].users_collection[0]; col.objects.link(o)
p=Vector((127.6,259.0,137.9)); t=Vector((132.6,268.5,136.3)); o.location=p; d=t-p
o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2)
print('CAM',n,flush=True)
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
