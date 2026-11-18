import bpy, math, os
from mathutils import Vector
sc=bpy.context.scene
C={'UB_CAM_oblique_Freeman_from_SW':((-150,-262,170),(-91,-200,138),30),
   'UB_CAM_eye_Freeman_S_end':((-98,-262,128),(-92,-215,137),28),
   'UB_CAM_closeup_Freeman_S_top':((-110,-245,148),(-92,-221,143),35)}
for n,(p,t,l) in C.items():
    o=bpy.data.objects.get(n)
    if not o:
        cd=bpy.data.cameras.new(n); o=bpy.data.objects.new(n,cd); sc.collection.objects.link(o)
    o['ub_obj']=1; o.location=p; o.rotation_euler=(Vector(t)-Vector(p)).to_track_quat('-Z','Y').to_euler(); o.data.lens=l
print('UB cams',len(C))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
