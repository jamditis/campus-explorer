import bpy, json
from mathutils import Vector as V
log=json.load(open('/workspace/nj-scenes/montclair-state/data/vt/vt_main.json'))
PW=V(log['PW']); PE=V(log['PE']); mid=(PW+PE)/2
out=V((0.228,0.974,0)).normalized(); d=V((-0.974,0.228,0)).normalized()
pos=mid+out*7.5+d*2.8; pos.z=131.45
tgt=mid+out*0.5; tgt.z=131.9
cd=bpy.data.cameras.new('VT_CAM_closeup_Freeman_N_entrance_steps'); cd.lens=28
cam=bpy.data.objects.new('VT_CAM_closeup_Freeman_N_entrance_steps',cd); cam['vt_obj']=1
bpy.data.collections['VT_Freeman_N_entrance_recess_UNVERIFIED'].objects.link(cam)
cam.location=pos
cam.rotation_euler=(tgt-pos).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
print('CAMOK',tuple(round(a,2) for a in pos))
