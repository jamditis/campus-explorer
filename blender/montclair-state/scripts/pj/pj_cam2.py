import bpy,sys
from mathutils import Vector
N='PJ_CAM_eye_feliciano_NW'
if N in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[N])
src=bpy.data.objects['PF_CAM_eye_feliciano_east']
cd=bpy.data.cameras.new(N); cd.lens=24; c=bpy.data.objects.new(N,cd); src.users_collection[0].objects.link(c)
s=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
x,y=-280.0,245.0
h=s.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
z=(h[1].z if h[0] else 134.0)+1.7
c.location=Vector((x,y,z)); tgt=Vector((-238,212,z+6))
c.rotation_euler=(tgt-c.location).to_track_quat('-Z','Y').to_euler()
print('PJCAM2',tuple(round(v,2) for v in c.location),h[4].name if h[0] else None)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
