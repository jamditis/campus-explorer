# sa cameras (REVERT=1 removes SA_CAM_*) + image path fix + library report
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
for o in [o for o in bpy.data.objects if o.name.startswith('SA_CAM')]:
    d=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(d)
im=bpy.data.images.get('annex_mural_arch_tile_mi.png')
if im: print('SA img',im.filepath,im.packed_file is not None)
for l in bpy.data.libraries:
    if 'montclair_north' in l.filepath:
        print('SA northlib users',l.users,[ (k,x.name) for k in ('objects','meshes','materials','node_groups','images','collections') for x in getattr(bpy.data,k) if x.library==l][:20])
if not REV:
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    def gz(x,y):
        h,l,*_=sc.ray_cast(dg,Vector((x,y,250)),Vector((0,0,-1))); return l.z if h else 139
    C={'SA_CAM_oblique_annex_from_SW':((-175,225,None,75),(-50,305,140),35),
       'SA_CAM_eye_annex_mural_from_W':((-128,300,1.7,0),(-92,318,142),28),
       'SA_CAM_eye_lowwall_deck_from_S':((-40,246,1.7,0),(-55,288,139.5),28),
       'SA_CAM_closeup_deck_lowwall':((-58,268,1.7,0),(-64,289,139.3),40)}
    for n,((x,y,eh,ah),t,lens) in C.items():
        z=gz(x,y)+(eh if eh else ah)
        cd=bpy.data.cameras.new(n); cd.lens=lens; cd.clip_end=6000; o=bpy.data.objects.new(n,cd); sc.collection.objects.link(o)
        o.location=(x,y,z); o.rotation_euler=(Vector(t)-Vector((x,y,z))).to_track_quat('-Z','Y').to_euler(); o['UNVERIFIED_sa']='sa camera'
        print('SA cam',n,round(z,2),'ground',round(gz(x,y),2))
    for x,y in [(-45,280),(-60,282),(-70,288),(-32,281),(-100,300),(0,265),(-55,310)]: print('SA gz',x,y,round(gz(x,y),2))
    pass
if os.environ.get("SAVE")=="1" or not REV: bpy.ops.wm.save_mainfile(); print("SAVED")
