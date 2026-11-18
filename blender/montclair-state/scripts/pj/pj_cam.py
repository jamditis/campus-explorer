import bpy,sys,math
from mathutils import Vector
N='PJ_CAM_closeup_feliciano_east_windows'
if N in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[N])
src=bpy.data.objects['PF_CAM_eye_feliciano_east']
cd=bpy.data.cameras.new(N); cd.lens=35; c=bpy.data.objects.new(N,cd)
src.users_collection[0].objects.link(c)
c.location=Vector((-186.0,206.5,141.2)); tgt=Vector((-192.5,209.5,143.8))
c.rotation_euler=(tgt-c.location).to_track_quat('-Z','Y').to_euler()
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PJCAM',len(bpy.data.objects))
