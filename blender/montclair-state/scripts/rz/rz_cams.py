# rz cameras (REVERT=1 removes RZ_CAM_*). Eye heights = raycast ground + 1.7 m.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
for o in [o for o in bpy.data.objects if o.name.startswith('RZ_CAM')]:
    d=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(d)
if not REV:
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    def gz(x,y):
        h,l,*_=sc.ray_cast(dg,Vector((x,y,250)),Vector((0,0,-1))); return l.z if h else 139
    C={'RZ_CAM_oblique_SC_from_SW':((-120,170,None,95),(-5,300,141),35),
       'RZ_CAM_eye_SC_entry_from_SSW':((-30,238,1.7,0),(-10,292,146.5),28),
       'RZ_CAM_eye_SC_from_E':((62,292,1.7,0),(5,305,145.5),30),
       'RZ_CAM_closeup_SC_entry':((-17,268,1.7,0),(-9,292,147),40)}
    for n,((x,y,eh,ah),t,lens) in C.items():
        z=gz(x,y)+(eh if eh else ah)
        cd=bpy.data.cameras.new(n); cd.lens=lens; cd.clip_end=6000; o=bpy.data.objects.new(n,cd); sc.collection.objects.link(o)
        o.location=(x,y,z); o.rotation_euler=(Vector(t)-Vector((x,y,z))).to_track_quat('-Z','Y').to_euler(); o['UNVERIFIED_rz']='rz camera'
        print('RZ cam',n,round(z,2))
    bpy.ops.wm.save_mainfile(); print('SAVED')
