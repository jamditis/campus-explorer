"""wo: named walkthrough camera presets + orbit flyover path (cameras/curve/empty only; no geometry, no materials)."""
import bpy, math
from mathutils import Vector
sc=bpy.context.scene
CN='WO_Walkthrough_presets_20261109wo'
col=bpy.data.collections.get(CN) or bpy.data.collections.new(CN)
if col.name not in sc.collection.children: sc.collection.children.link(col)
PRESETS=[('WALK_01_campus_overview_aerial_from_SW','CAM_aerial_oblique_SW'),
 ('WALK_02_approach_from_Normal_Ave_Freeman_S','UB_CAM_eye_Freeman_S_end'),
 ('WALK_03_CCOM_hero_entrance','CAM_eye_CCOM_entrance'),
 ('WALK_04_quad_Student_Center_entry_from_SSW','RZ_CAM_eye_SC_entry_from_SSW'),
 ('WALK_05_Schmitt_pavilion_front','OI_CAM_eye_schmitt_pavilion_front'),
 ('WALK_06_CELS_from_W','QM_CAM_eye_cels_from_west'),
 ('WALK_07_dorm_row_Blanton_from_S','TJ_CAM_eye_Webster_lawn_Blanton_from_S'),
 ('WALK_08_College_Hall_from_S','TW_CAM_eye_CollegeHall_from_S')]
made=[]
for new,src in PRESETS:
    s=bpy.data.objects.get(src); assert s and s.type=='CAMERA', src
    o=bpy.data.objects.get(new)
    if o is None:
        d=s.data.copy(); d.name=new+'_data'; o=bpy.data.objects.new(new,d); col.objects.link(o)
    o.matrix_world=s.matrix_world.copy(); o.data.clip_end=max(o.data.clip_end,30000)
    o['wo_source_camera']=src; o['wo_preset']=True; made.append(new)
# orbit flyover
C=Vector((20.0,100.0,0.0)); R=380.0; Z=300.0
tgt=bpy.data.objects.get('WALK_target_campus_center') or bpy.data.objects.new('WALK_target_campus_center',None)
if tgt.name not in col.objects: col.objects.link(tgt)
tgt.location=(C.x,C.y,135.0); tgt.empty_display_size=10
cu=bpy.data.curves.get('WALK_PATH_orbit_campus_data') or bpy.data.curves.new('WALK_PATH_orbit_campus_data','CURVE')
cu.splines.clear(); cu.dimensions='3D'; sp=cu.splines.new('NURBS'); N=16
sp.points.add(N-1)
for i in range(N):
    a=2*math.pi*i/N - math.radians(131)   # start near the SW overview bearing
    sp.points[i].co=(C.x+R*math.cos(a),C.y+R*math.sin(a),Z,1)
sp.use_cyclic_u=True; sp.order_u=4; cu.path_duration=720; cu.use_path=True
po=bpy.data.objects.get('WALK_PATH_orbit_campus') or bpy.data.objects.new('WALK_PATH_orbit_campus',cu)
if po.name not in col.objects: col.objects.link(po)
po.hide_render=True
cd=bpy.data.cameras.get('WALK_09_orbit_flyover_data') or bpy.data.cameras.new('WALK_09_orbit_flyover_data')
cd.lens=32; cd.clip_end=30000
cam=bpy.data.objects.get('WALK_09_orbit_flyover') or bpy.data.objects.new('WALK_09_orbit_flyover',cd)
if cam.name not in col.objects: col.objects.link(cam)
cam.location=(0,0,0); cam.rotation_euler=(0,0,0)
cam.constraints.clear()
fp=cam.constraints.new('FOLLOW_PATH'); fp.target=po; fp.use_fixed_location=True; fp.use_curve_follow=False
fp.offset_factor=0.0; fp.keyframe_insert('offset_factor',frame=1)
fp.offset_factor=1.0; fp.keyframe_insert('offset_factor',frame=721)
for fc in cam.animation_data.action.fcurves:
    for k in fc.keyframe_points: k.interpolation='LINEAR'
tt=cam.constraints.new('TRACK_TO'); tt.target=tgt; tt.track_axis='TRACK_NEGATIVE_Z'; tt.up_axis='UP_Y'
cam['wo_preset']=True; made.append('WALK_09_orbit_flyover')
txt=bpy.data.texts.get('WALKTHROUGH_PRESETS.md') or bpy.data.texts.new('WALKTHROUGH_PRESETS.md')
txt.clear()
txt.write('# Walkthrough camera presets (session wo, 2026-11-09, UNVERIFIED framing)\n\nCollection: '+CN+'\n\n'+
 '\n'.join(f'- {n}: copy of {s}' for n,s in PRESETS)+
 '\n- WALK_09_orbit_flyover: 720-frame (30 s at 24 fps) orbit, radius 380 m at z 300 m around (20,100), tracking WALK_target_campus_center; Follow Path offset keyed 0..1 over frames 1..721.\n'+
 '\nStation preset lives in north/montclair_north.blend (CAM_eye_station_platform / CAM_aerial_station_trains_20261014).\nLighting presets: see later sessions.\n')
sc.frame_set(1)
bpy.ops.wm.save_mainfile()
print('WO_OK',made,len(bpy.data.objects))
