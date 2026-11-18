"""wo pass 2: swap two weak presets (self-review) for better-framed source cams."""
import bpy
col=bpy.data.collections['WO_Walkthrough_presets_20261109wo']
SWAP={'WALK_04_quad_Student_Center_entry_from_SSW':('WALK_04_quad_Student_Center_from_E','RZ_CAM_eye_SC_from_E'),
      'WALK_07_dorm_row_Blanton_from_S':('WALK_07_dorm_row_Bohn_from_W','TK_CAM_eye_Bohn_from_W')}
for old,(new,src) in SWAP.items():
    o=bpy.data.objects.get(old)
    if o: d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    s=bpy.data.objects[src]; d=s.data.copy(); d.name=new+'_data'; d.clip_end=max(d.clip_end,30000)
    n=bpy.data.objects.new(new,d); col.objects.link(n); n.matrix_world=s.matrix_world.copy(); n['wo_source_camera']=src; n['wo_preset']=True
t=bpy.data.texts['WALKTHROUGH_PRESETS.md']; s=t.as_string()
s=s.replace('- WALK_04_quad_Student_Center_entry_from_SSW: copy of RZ_CAM_eye_SC_entry_from_SSW','- WALK_04_quad_Student_Center_from_E: copy of RZ_CAM_eye_SC_from_E')
s=s.replace('- WALK_07_dorm_row_Blanton_from_S: copy of TJ_CAM_eye_Webster_lawn_Blanton_from_S','- WALK_07_dorm_row_Bohn_from_W: copy of TK_CAM_eye_Bohn_from_W')
t.clear(); t.write(s)
bpy.ops.wm.save_mainfile()
print('WO2_OK',sorted(o.name for o in col.objects),len(bpy.data.objects))
